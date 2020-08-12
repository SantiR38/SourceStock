from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.template import Template, Context, loader
from django.core.exceptions import ObjectDoesNotExist, FieldError
from erp.forms import FormVenta, FormNuevoArticulo, FormEntrada, FormCliente, FormBusqueda, FormFiltroFecha, FormProveedor
from erp.models import Article, ArtState, Entrada, DetalleEntrada, Venta, DetalleVenta, Perdida, DetallePerdida, Cliente, Proveedor
from erp.functions import stock_total, add_art_state, porcentaje_ganancia, inventario, venta_activa, compra_activa, buscar_cliente, buscar_proveedor, dni_cliente, campos_sin_iva, precio_final, emitir_recibo, nombre_proveedor
from datetime import date
from decimal import *


def agregar_articulo(request):
    template = loader.get_template('agregar_modificar.html')
    miFormulario = FormNuevoArticulo()
    lista = []
    ctx = {
        "datos_generales": stock_total(),
        "form": miFormulario,
        "titulo": "Agregar artículo"
    }
    # Manejo del formulario de compra
    if request.method == "POST":
        miFormulario = FormNuevoArticulo(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data
            try:
                new_article = Article.objects.get(codigo=infForm['codigo'])
                ctx['mensaje'] = "El código ya está siendo utilizado por otro producto."
            except ObjectDoesNotExist as DoesNotExist:

                if infForm['costo'] != None and infForm['costo_sin_iva'] != None:
                    if porcentaje_ganancia(infForm['costo_sin_iva'], 21) == infForm['costo']:
                        new_article = Article.objects.create(codigo=infForm['codigo'],
                                    descripcion=infForm['descripcion'],
                                    costo_sin_iva=infForm['costo_sin_iva'],
                                    costo=infForm['costo'],
                                    porcentaje_ganancia=infForm['porcentaje_ganancia'],
                                    precio_sin_iva=porcentaje_ganancia(infForm['costo_sin_iva'], infForm['porcentaje_ganancia']),
                                    precio=porcentaje_ganancia(infForm['costo'], infForm['porcentaje_ganancia']),
                                    seccion=infForm['seccion'],
                                    stock=infForm['stock'])
                        return redirect('control_inventario')
                    else:
                        ctx['mensaje'] = "PROBLEMA: El costo final no es el costo neto + IVA. Se recomienda llenar solo uno de estos dos campos."

                elif infForm['costo'] != None or infForm['costo_sin_iva'] != None:
                    if infForm['costo_sin_iva'] != None:
                        new_article = Article.objects.create(codigo=infForm['codigo'],
                                                            descripcion=infForm['descripcion'],
                                                            costo_sin_iva=infForm['costo_sin_iva'],
                                                            costo=porcentaje_ganancia(infForm['costo_sin_iva'], 21),
                                                            precio_sin_iva=porcentaje_ganancia(infForm['costo_sin_iva'], infForm['porcentaje_ganancia']),
                                                            precio=porcentaje_ganancia(infForm['costo_sin_iva'], infForm['porcentaje_ganancia']) * Decimal(1.21),
                                                            porcentaje_ganancia=infForm['porcentaje_ganancia'],
                                                            seccion=infForm['seccion'],
                                                            stock=infForm['stock'])
                        return redirect('control_inventario')
                    else:
                        new_article = Article.objects.create(codigo=infForm['codigo'],
                                                            descripcion=infForm['descripcion'],
                                                            costo_sin_iva=infForm['costo'] / Decimal(1.21),
                                                            costo=infForm['costo'],
                                                            precio_sin_iva=porcentaje_ganancia(infForm['costo'], infForm['porcentaje_ganancia']) / Decimal(1.21),
                                                            precio=porcentaje_ganancia(infForm['costo'], infForm['porcentaje_ganancia']),
                                                            porcentaje_ganancia=infForm['porcentaje_ganancia'],
                                                            seccion=infForm['seccion'],
                                                            stock=infForm['stock'])
                        return redirect('control_inventario')
                else:
                    ctx['mensaje'] = "PROBLEMA: Debes rellenar uno de los dos costos."

                ctx['datos_generales'] = stock_total() # Actualiza el stock cuando se hace la compra, asi no va atrasado

                miFormulario = FormNuevoArticulo()
    else:
        miFormulario = FormNuevoArticulo()

    return HttpResponse(template.render(ctx, request))


def entrada(request):
    template = loader.get_template('entrada.html')
    miFormulario = FormEntrada({'cantidad': 1, 'proveedor': nombre_proveedor()})
    estado = ArtState.objects.get(nombre="Active") # Creamos un ArtState instance para definir una transacción Activa
    lista = []
    ctx = {
        "articulo_a_comprar": compra_activa()[0],
        "datos_generales": stock_total(),
        "form": miFormulario,
        "total": compra_activa()[1].total,
        "porcentaje_inexistente": "",
        "proveedor": ""
    }
    if compra_activa()[1].proveedor != None:
        ctx['proveedor'] = compra_activa()[1].proveedor.nombre

    if request.method == "POST":
        miFormulario = FormEntrada(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data # Sacamos los datos del formulario en un diccionario y lo metemos a una variable
            
            try: # Si ya hay un objeto activo, solo agregarle elementos de tipo detalle_entrada a su id
                    nueva_venta = Entrada.objects.get(id_state=estado)
                    nueva_venta.proveedor=buscar_proveedor(infForm['proveedor'])
                    nueva_venta.save()
            except ObjectDoesNotExist as DoesNotExist:
                nueva_venta = Entrada.objects.create(fecha=infForm['fecha'],
                                                        total=0,
                                                        id_state=estado,
                                                        proveedor=buscar_proveedor(infForm['proveedor'])) # Iniciar un objeto de tipo entrada (id(auto), fecha, id_state=1(active), total=0)

            try: # Si el producto existe en la base de datos
                new_article = Article.objects.get(codigo=infForm['codigo']) # Llamamos al objeto desde la db que tenga el mismo codigo que en
                                                                            # el formulario y lo metemos como QuerySet en una variable.
                if new_article.porcentaje_ganancia == None:
                    ctx["porcentaje_inexistente"] = "Este producto no tiene porcentaje de ganancia. Agrégalo en la sección 'Agregar o modificar' antes de continuar."
                
                if infForm['costo'] != None and infForm['costo_sin_iva'] != None:

                    if porcentaje_ganancia(infForm['costo_sin_iva'], 21) == infForm['costo']:
                        producto_leido = DetalleEntrada.objects.create(costo_sin_iva=infForm['costo_sin_iva'], # Iniciar un objeto de tipo detalle_entrada
                                                                    costo_unitario = infForm['costo'],
                                                                    cantidad=infForm['cantidad'],
                                                                    id_entrada=Entrada.objects.get(id_state=estado),
                                                                    id_producto=Article.objects.get(codigo=infForm['codigo']))
                        ctx['inexistente'] = ''
                    else:
                        ctx['inexistente'] = "PROBLEMA: El costo final no es el costo neto + IVA. Se recomienda llenar solo uno de estos dos campos."


                elif infForm['costo'] != None or infForm['costo_sin_iva'] != None:
                    if infForm['costo_sin_iva'] != None:
                        producto_leido = DetalleEntrada.objects.create(costo_sin_iva=infForm['costo_sin_iva'], # Iniciar un objeto de tipo detalle_entrada
                                                                costo_unitario = porcentaje_ganancia(infForm['costo_sin_iva'], 21),
                                                                cantidad=infForm['cantidad'],
                                                                id_entrada=Entrada.objects.get(id_state=estado),
                                                                id_producto=Article.objects.get(codigo=infForm['codigo']))
                    else:
                        producto_leido = DetalleEntrada.objects.create(costo_unitario=infForm['costo'], # Iniciar un objeto de tipo detalle_entrada
                                                                    costo_sin_iva=infForm['costo'] / Decimal(1.21),
                                                                    cantidad=infForm['cantidad'],
                                                                    id_entrada=Entrada.objects.get(id_state=estado),
                                                                    id_producto=Article.objects.get(codigo=infForm['codigo']))
                                    # Se suman los precios unitarios al precio total de la compra
                    ctx['inexistente'] = ''
                else:
                    ctx['inexistente'] = "Debes rellenar uno de los dos costos."

            except ObjectDoesNotExist as DoesNotExist: # Si el producto no existe en la base de datos
                ctx['inexistente'] = 'Artículo inexistente, debe agregarlo en la sección "Control de inventario/Agregar artículo". El resto de la compra seguirá guardada.'
            
            lista = DetalleEntrada.objects.filter(id_entrada = nueva_venta) 
            nueva_venta.total = 0
            for i in lista:
                nueva_venta.total += (i.costo_unitario * i.cantidad)
            nueva_venta.save()
            ctx['total'] = nueva_venta.total
            ctx['articulo_a_comprar'] = lista

            miFormulario = FormEntrada({'cantidad': 1, 'proveedor': nombre_proveedor()})

            if compra_activa()[1].proveedor != None:
                ctx['proveedor'] = compra_activa()[1].proveedor.nombre
            
            return HttpResponse(template.render(ctx, request))
    else:
        # Es es formulario que se muestra antes de enviar la info. La cantidad por defecto de articulos a comprar es 1.
        miFormulario = FormEntrada({'cantidad': 1, 'proveedor': nombre_proveedor()})

    return HttpResponse(template.render(ctx, request))


def venta(request):
    template = loader.get_template('venta.html')
    miFormulario = FormVenta({'cantidad': 1, 'dni_cliente': dni_cliente()})
    estado = ArtState.objects.get(nombre="Active") # Creamos un ArtState instance para definir una transacción Activa
    lista = []
    ctx = {
        "articulo_a_vender": venta_activa()[0],
        "datos_generales": stock_total(),
        "form": miFormulario,
        "total": venta_activa()[1].total,
        "cliente": ""
    }
    if venta_activa()[1].cliente != None:
        ctx['cliente'] = venta_activa()[1].cliente.nombre + " " + venta_activa()[1].cliente.apellido
    
    if request.method == "POST":
        miFormulario = FormVenta(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data # Sacamos los datos del formulario en un diccionario y lo metemos a una variable

            try: # Si el producto existe en la base de datos
                new_article = Article.objects.get(codigo=infForm['codigo']) # Llamamos al objeto desde la db que tenga el mismo codigo que en
                                                                            # el formulario y lo metemos como QuerySet en una variable.
                try: # Si ya hay un objeto activo, solo agregarle elementos de tipo detalle_Venta a su id
                    nueva_venta = Venta.objects.get(id_state=estado)
                    nueva_venta.cliente = buscar_cliente(infForm['dni_cliente'])
                    nueva_venta.save()
                except ObjectDoesNotExist as DoesNotExist: # Si no hay ninguno activo, crearlo.
                    nueva_venta = Venta.objects.create(fecha=date.today(),
                                                         total=0,
                                                         id_state=estado,
                                                         cliente=buscar_cliente(infForm['dni_cliente'])) # Iniciar un objeto de tipo Venta (id(auto), fecha, id_state=1(active), total=0)

                producto_leido = DetalleVenta.objects.create(costo_unitario=new_article.costo, # Iniciar un objeto de tipo detalle_venta
                                                               precio_unitario=new_article.precio,
                                                               cantidad=infForm['cantidad'],
                                                               id_venta=Venta.objects.get(id_state=estado),
                                                               id_producto=Article.objects.get(codigo=infForm['codigo']))
            # Se suman los precios unitarios al precio total de la venta
                lista = DetalleVenta.objects.filter(id_venta = nueva_venta) 
                nueva_venta.total = 0
                for i in lista:
                    nueva_venta.total += (i.precio_unitario * i.cantidad)
                nueva_venta.save()
                ctx['total'] = nueva_venta.total
                ctx['inexistente'] = ''
                ctx['articulo_a_vender'] = lista
            except ObjectDoesNotExist as DoesNotExist: # Si el producto no existe en la base de datos
                ctx['inexistente'] = 'Artículo inexistente, debe agregarlo en la sección "Control de inventario/Agregar artículo". El resto de la venta seguirá guardada.'

            miFormulario = FormVenta({'cantidad': 1, 'dni_cliente': dni_cliente()})
            ctx['form'] = miFormulario
            if venta_activa()[1].cliente != None:
                ctx['cliente'] = venta_activa()[1].cliente.nombre + " " + venta_activa()[1].cliente.apellido
            
            return HttpResponse(template.render(ctx, request))
    else:
        # Es es formulario que se muestra antes de enviar la info. La cantidad por defecto de articulos a vender es 1.
        miFormulario = FormVenta({'cantidad': 1, 'dni_cliente': dni_cliente()})

    return HttpResponse(template.render(ctx, request))


def cancelar_unidad(request, codigo_articulo):
    try:
        articulo_staging = DetalleVenta.objects.get(id=codigo_articulo)
    except ObjectDoesNotExist as DoesNotExist:
        pass
    else:
        articulo_staging.delete()
    return redirect('venta')


def transaccion_exitosa(request):
    template = loader.get_template('mensaje.html')
    ctx = {'mensaje': 'Su transacción fue un éxito.',
           'redireccion': 'Volviendo a la página de ventas...'}

    estado = ArtState.objects.get(nombre="Active")
    try:
        nueva_venta = Entrada.objects.get(id_state=estado)

        producto_leido = DetalleEntrada.objects.filter(id_entrada=nueva_venta) # Se crea un QuerySet para sacar datos de cada producto comprado

        try:
            for j in producto_leido: # Esto es simplemente para que cancele la compra completa y no se actualicen el stock y precio solo de algunos productos
                test_porcentaje = j.id_producto.porcentaje_ganancia * 1 # Es una multiplicacion que solo sirve para poner en evidencia el error (porque un numero no se puede multiplicar por 'None')
            for i in producto_leido: # Se actualiza el costo y el stock de cada objeto Article
                i.id_producto.costo_sin_iva = i.costo_sin_iva
                i.id_producto.costo = i.costo_unitario
                i.id_producto.precio_sin_iva = porcentaje_ganancia(i.costo_sin_iva, i.id_producto.porcentaje_ganancia)
                i.id_producto.precio = porcentaje_ganancia(i.costo_unitario, i.id_producto.porcentaje_ganancia)
                i.id_producto.stock += i.cantidad
                i.id_producto.save()
            
            nueva_venta.id_state = ArtState.objects.get(nombre="Inactive") # Pasamos la entrada a modo inactivo
            nueva_venta.save() # Hace que esa entrada pase a estar inactiva
        except TypeError:
            ctx['mensaje'] = 'Error. Uno o varios artículos no poseen porcentaje de ganancia. Agregalos en "Agregar o Modificar" Luego registra nuevamente la compra.'
            nueva_venta = Entrada.objects.get(id_state=estado)
            nueva_venta.delete() # Se borra el registro de la entrada que está activa, y los detalles se borran automaticamente al estar en modo CASCADE (models.py)


    except ObjectDoesNotExist as DoesNotExist:
        ctx['mensaje'] = 'Error 404. Tu solicitud no fue encontrada.'


    return HttpResponse(template.render(ctx, request))


def venta_exitosa(request):
    template = loader.get_template('mensaje.html')
    ctx = {'mensaje': 'Su transacción fue un éxito.',
           'hay_recibo': False}

    estado = ArtState.objects.get(nombre="Active")
    try:
        nueva_venta = Venta.objects.get(id_state=estado)

        producto_leido = DetalleVenta.objects.filter(id_venta=nueva_venta) # Se crea un QuerySet para sacar datos de cada producto comprado
        
        if producto_leido.exists():
            for i in producto_leido: # Se actualiza  el stock de cada objeto Article
                i.id_producto.stock -= i.cantidad
                i.id_producto.save()
            
            nueva_venta.id_state = ArtState.objects.get(nombre="Inactive") # Pasamos la entrada a modo inactivo
            nueva_venta.save() # Hace que esa entrada pase a estar inactiva
            ctx['hay_recibo'] = True
        else:
            ctx['mensaje'] = 'Error 404. Tu solicitud no fue encontrada.'

    except ObjectDoesNotExist as DoesNotExist:
        ctx['mensaje'] = 'Error 404. Tu solicitud no fue encontrada.'
        
    ctx['id_venta'] = nueva_venta.id
    return HttpResponse(template.render(ctx, request))


def cancelar(request):
    template = loader.get_template('mensaje.html')
    ctx = {'mensaje': 'Se ha cancelado la transacción.',
           'redireccion': 'Volviendo a la página de ventas...'}
    
    estado = ArtState.objects.get(nombre="Active")
    try:
        nueva_venta = Entrada.objects.get(id_state=estado)
        nueva_venta.delete() # Se borra el registro de la entrada que está activa, y los detalles se borran automaticamente al estar en modo CASCADE (models.py)
    except ObjectDoesNotExist as DoesNotExist:
        try:
            nueva_venta = Venta.objects.get(id_state=estado)
            nueva_venta.delete()
        except ObjectDoesNotExist as DoesNotExist:
            ctx['mensaje'] = 'Error 404. Tu solicitud no fue encontrada.'

    return HttpResponse(template.render(ctx, request))


def cliente(request):
    template = loader.get_template('agregar_modificar.html')
    miFormulario = FormCliente()
    lista = []
    ctx = {
        "articulo_a_vender": lista,
        "datos_generales": stock_total(),
        "form": miFormulario,
        "mensaje": "",
        "titulo": "Gestión de clientes"
    }

    if request.method == "POST":
        miFormulario = FormCliente(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data # Sacamos los datos del formulario en un diccionario y lo metemos a una variable
            
            try: # Si el cliente existe en la base de datos
                new_client = Cliente.objects.get(dni=infForm['dni'])
                ctx['mensaje'] = "El cliente ya existe"
                
            except ObjectDoesNotExist as DoesNotExist: # Si el cliente no existe en la base de datos, crearlo
                new_client = Cliente.objects.create(nombre=infForm['nombre'],
                                                    apellido=infForm['apellido'],
                                                    condicion_iva=infForm['condicion_iva'],
                                                    dni=infForm['dni'],
                                                    cuit=infForm['cuit'],
                                                    direccion=infForm['direccion'],
                                                    telefono=infForm['telefono'],
                                                    email=infForm['email'])

                ctx['mensaje'] = 'El cliente fue agregado correctamente.'

            miFormulario = FormCliente()

    return HttpResponse(template.render(ctx, request))


def control_inventario(request):
    template = loader.get_template('control_inventario.html')
    miFormulario = FormBusqueda()
    ctx = {
        "datos_generales": stock_total(),
        "articulos": inventario(),
        "form": miFormulario
    }

    if request.method == "POST":
        miFormulario = FormBusqueda(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data
            resultado = Article.objects.filter(codigo=int(infForm['buscar'])) # Código
            ctx["articulos"] = resultado
    else:
        miFormulario = FormBusqueda()

    return HttpResponse(template.render(ctx, request))


def articulo(request, codigo_articulo):
    template = loader.get_template('agregar_modificar.html')
    try:
        new_article = Article.objects.get(codigo=codigo_articulo)
    except ObjectDoesNotExist as DoesNotExist:
            template = loader.get_template('mensaje.html') # La redirección se hace con JavaScript en este template luego de 5 segundos.
            ctx = {'mensaje': 'Error 404. No se encontró el artículo.',
                'redireccion': 'Volviendo a la página de ventas...'}
            return HttpResponse(template.render(ctx, request))
    else:  
        detalles_formulario = {
            'codigo': new_article.codigo,
            'descripcion': new_article.descripcion,
            'costo': new_article.costo,
            'porcentaje_ganancia': new_article.porcentaje_ganancia,
            'seccion': new_article.seccion,
            'stock': new_article.stock
        }
        miFormulario = FormNuevoArticulo(detalles_formulario)
        ctx = {
            "datos_generales": stock_total(),
            "articulos": inventario(),
            "form": miFormulario,
            "titulo": "Modificar Artículo"
        }
        
        if request.method == "POST":
            miFormulario = FormNuevoArticulo(request.POST)
            if miFormulario.is_valid():
                infForm = miFormulario.cleaned_data
                
                if infForm['costo'] != None and infForm['costo_sin_iva'] != None:
                    if porcentaje_ganancia(infForm['costo_sin_iva'], 21) == infForm['costo']:
                        
                        new_article.codigo = infForm['codigo']
                        if infForm['descripcion'] != "":
                            new_article.descripcion = infForm['descripcion']
                        new_article.costo_sin_iva = infForm['costo_sin_iva']
                        new_article.costo = infForm['costo']
                        new_article.porcentaje_ganancia = infForm['porcentaje_ganancia']
                        new_article.precio_sin_iva = porcentaje_ganancia(infForm['costo_sin_iva'], infForm['porcentaje_ganancia'])
                        new_article.precio = porcentaje_ganancia(infForm['costo'], infForm['porcentaje_ganancia']) # costo+(costo*porcentaje/100)
                        if infForm['seccion'] != "":
                            new_article.seccion = infForm['seccion']
                        new_article.stock = infForm['stock']
                        new_article.save() # Guardamos los cambios de la linea anterior en la base de datos
                        
                        return redirect('control_inventario')
                    else:
                        ctx['mensaje'] = "PROBLEMA: El costo final no es el costo neto + IVA. Se recomienda llenar solo uno de estos dos campos."
                        miFormulario = FormNuevoArticulo(detalles_formulario)

                elif infForm['costo'] != None or infForm['costo_sin_iva'] != None:
                    if infForm['costo_sin_iva'] != None:

                        new_article.codigo = infForm['codigo']
                        if infForm['descripcion'] != "":
                            new_article.descripcion = infForm['descripcion']
                        new_article.costo_sin_iva = infForm['costo_sin_iva']
                        new_article.costo = porcentaje_ganancia(infForm['costo_sin_iva'], 21)
                        new_article.porcentaje_ganancia = infForm['porcentaje_ganancia']
                        new_article.precio_sin_iva = porcentaje_ganancia(infForm['costo_sin_iva'], infForm['porcentaje_ganancia'])
                        new_article.precio = porcentaje_ganancia(infForm['costo_sin_iva'], infForm['porcentaje_ganancia']) * Decimal(1.21)
                        if infForm['seccion'] != "":
                            new_article.seccion = infForm['seccion']
                        new_article.stock = infForm['stock']
                        new_article.save() # Guardamos los cambios de la linea anterior en la base de datos

                        return redirect('control_inventario')
                        
                    else: # Si el costo esta rellenado
                        
                        new_article.codigo = infForm['codigo']
                        if infForm['descripcion'] != "":
                            new_article.descripcion = infForm['descripcion']
                        new_article.costo_sin_iva = infForm['costo'] / Decimal(1.21)
                        new_article.costo = infForm['costo']
                        new_article.porcentaje_ganancia = infForm['porcentaje_ganancia']
                        new_article.precio_sin_iva = porcentaje_ganancia(infForm['costo'], infForm['porcentaje_ganancia']) / Decimal(1.21)
                        new_article.precio = porcentaje_ganancia(infForm['costo'], infForm['porcentaje_ganancia'])
                        if infForm['seccion'] != "":
                            new_article.seccion = infForm['seccion']
                        new_article.stock = infForm['stock']
                        new_article.save() # Guardamos los cambios de la linea anterior en la base de datos

                        return redirect('control_inventario')

                else:
                    ctx['mensaje'] = "PROBLEMA: Debes rellenar uno de los dos costos."
                    miFormulario = FormNuevoArticulo(detalles_formulario)

        else:
            miFormulario = FormNuevoArticulo(detalles_formulario)

    return HttpResponse(template.render(ctx, request))


def historial_ventas(request):
    template = loader.get_template('historial_ventas.html')
    miFormulario = FormFiltroFecha()
    venta_historica = Venta.objects.all().order_by('-fecha', '-id') # Trae todos los registros para mostrar en el historial y los ordena por fecha y por id.
    if venta_historica.exists():
        ultimas_ventas = []
        x = 0
        for i in venta_historica: # Este bucle solo selecciona una cantidad limitada de ventas para mostrar
            ultimas_ventas.append(i)
            x += 1
            if x == 50:
                break
        ctx = {
            "datos_generales": stock_total(),
            "venta": ultimas_ventas,
            "venta_historica": venta_historica,
            "form": miFormulario
        }
        # Filtro fecha
        if request.method == "POST":
            miFormulario = FormFiltroFecha(request.POST)
            if miFormulario.is_valid():
                infForm = miFormulario.cleaned_data
                ctx["venta"] = Venta.objects.filter(fecha__range=[infForm['fecha_inicial'], infForm['fecha_final']]).order_by('-fecha', '-id')
        else:
            miFormulario = FormFiltroFecha()
        # !filtro fecha

        return HttpResponse(template.render(ctx, request))

    else:
        return redirect('venta_exitosa')


def recibo(request, id_venta):
    try:
        return FileResponse(emitir_recibo(id_venta), as_attachment=False, filename='hello.pdf')
    except ObjectDoesNotExist as DoesNotExist :
        return redirect('transaccion_exitosa')
    

def proveedor(request):
    template = loader.get_template('agregar_modificar.html')
    miFormulario = FormProveedor()
    lista = []
    ctx = {
        "articulo_a_vender": lista,
        "datos_generales": stock_total(),
        "form": miFormulario,
        "mensaje": "",
        "titulo": "Gestión de proveedores"
    }

    if request.method == "POST":
        miFormulario = FormProveedor(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data # Sacamos los datos del formulario en un diccionario y lo metemos a una variable
            
            try: # Si el Proveedor existe en la base de datos
                new_proveedor = Proveedor.objects.get(nombre=infForm['nombre'])
                ctx['mensaje'] = "El proveedor ya existe"
                
            except ObjectDoesNotExist as DoesNotExist: # Si el Proveedor no existe en la base de datos, crearlo
                new_proveedor = Proveedor.objects.create(nombre=infForm['nombre'],
                                                    condicion_iva=infForm['condicion_iva'],
                                                    cuit=infForm['cuit'],
                                                    direccion=infForm['direccion'],
                                                    telefono=infForm['telefono'],
                                                    email=infForm['email'])

                ctx['mensaje'] = 'El proveedor fue agregado correctamente.'

            miFormulario = FormProveedor()

    return HttpResponse(template.render(ctx, request))


def script_actualizacion(request):
    template = loader.get_template('mje_sin_redireccion.html')
    ctx = {'titulo': 'Se agregaron los nuevos valores',
           'mensaje': 'Checkear en DB...'}
    campos_sin_iva()
    if not ArtState.objects.all().exists():
        add_art_state()
    

    return HttpResponse(template.render(ctx, request))

