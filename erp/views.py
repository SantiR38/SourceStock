from datetime import date
from decimal import Decimal

from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse, HttpResponseRedirect
from django.template import Template, Context, loader
from django.core.exceptions import ObjectDoesNotExist, FieldError
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from erp.forms import FormVenta, FormNuevoArticulo, FormEntrada, FormCliente
from erp.forms import FormBusqueda, FormFiltroFecha, FormProveedor
from erp.models import Article, ArtState, Entrada, DetalleEntrada, Venta
from erp.models import DetalleVenta, Perdida, DetallePerdida, Cliente, Proveedor
from erp.functions import stock_total, add_art_state, porcentaje_ganancia
from erp.functions import inventario, venta_activa, compra_activa, buscar_cliente
from erp.functions import crear_articulo, comprar_articulo, buscar_proveedor
from erp.functions import dni_cliente, campos_sin_iva, precio_final, emitir_recibo
from erp.functions import nombre_proveedor, emitir_detalle_entrada


# Funciones para administrar las compras o entradas.
@login_required
def entrada(request):
    template = loader.get_template('entrada.html')
    miFormulario = FormEntrada({'cantidad': 1, 'proveedor': nombre_proveedor()})
    # Creamos un ArtState instance para definir una transacción Activa
    estado = ArtState.objects.get(nombre="Active")
    lista = []
    ctx = {
        "articulo_a_comprar": compra_activa()[0],
        "datos_generales": stock_total(),
        "form": miFormulario,
        "total": compra_activa()[1].total,
        "porcentaje_inexistente": "",
        "proveedor": ""
    }
    if compra_activa()[1].proveedor is not None:
        ctx['proveedor'] = compra_activa()[1].proveedor.nombre

    if request.method == "POST":
        miFormulario = FormEntrada(request.POST)
        if miFormulario.is_valid():
            # Sacamos los datos del formulario en un diccionario y lo metemos a una variable
            infForm = miFormulario.cleaned_data
            # Si ya hay un objeto activo, solo agregarle
            # elementos de tipo detalle_entrada a su id
            try:
                nueva_venta = Entrada.objects.get(id_state=estado)
                nueva_venta.proveedor = buscar_proveedor(infForm['proveedor'])
                nueva_venta.save()
            except ObjectDoesNotExist as DoesNotExist:
                nueva_venta = Entrada.objects.create(fecha=infForm['fecha'],
                                                     total=0,
                                                     id_state=estado,
                                                     proveedor=buscar_proveedor(infForm['proveedor']))
            try: # Si el producto existe en la base de datos
                # Llamamos al objeto desde la db que tenga el mismo codigo que en
                # el formulario y lo metemos como QuerySet en una variable.
                new_article = Article.objects.get(codigo=infForm['codigo'])
                if new_article.porcentaje_ganancia is None:
                    ctx["porcentaje_inexistente"] = "Este producto no tiene porcentaje de ganancia. Agrégalo en la sección 'Agregar o modificar' antes de continuar."
                if infForm['costo'] is not None and infForm['costo_sin_iva'] is not None:
                    ctx['inexistente'] = "PROBLEMA: Los campos costo final y costo neto + IVA estan completados. Debes llenar solo uno de estos dos campos."
                elif infForm['costo'] is not None or infForm['costo_sin_iva'] is not None:
                    DetalleEntrada.objects.create(costo_sin_iva=comprar_articulo(infForm)['costo_sin_iva'], # Iniciar un objeto de tipo detalle_entrada
                                                  costo_unitario=comprar_articulo(infForm)['costo'],
                                                  cantidad=comprar_articulo(infForm)['cantidad'],
                                                  id_entrada=Entrada.objects.get(id_state=estado),
                                                  id_producto=Article.objects.get(codigo=infForm['codigo']))
                    ctx['inexistente'] = ''
                else:
                    ctx['inexistente'] = "Debes rellenar uno de los dos costos."

            except ObjectDoesNotExist as DoesNotExist: # Si el producto no existe en la base de datos
                ctx['inexistente'] = 'Artículo inexistente, debe agregarlo en la sección "Control de inventario/Agregar artículo". El resto de la compra seguirá guardada.'
            lista = DetalleEntrada.objects.filter(id_entrada=nueva_venta)
            nueva_venta.total = 0
            for i in lista:
                nueva_venta.total += (i.costo_unitario * i.cantidad) # Se suman los precios unitarios al precio total de la compra
            nueva_venta.save()
            ctx['total'] = nueva_venta.total
            ctx['articulo_a_comprar'] = lista

            miFormulario = FormEntrada({'cantidad': 1, 'proveedor': nombre_proveedor()})

            if compra_activa()[1].proveedor is not None:
                ctx['proveedor'] = compra_activa()[1].proveedor.nombre
            return HttpResponse(template.render(ctx, request))
    else:
        # Es es formulario que se muestra antes de enviar la info. La cantidad por defecto de articulos a comprar es 1.
        miFormulario = FormEntrada({'cantidad': 1, 'proveedor': nombre_proveedor()})

    return HttpResponse(template.render(ctx, request))

@login_required
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
                i.id_producto.precio_descontado = porcentaje_ganancia(i.id_producto.precio, -i.id_producto.porcentaje_descuento)
                i.id_producto.stock += i.cantidad
                i.id_producto.save()

            nueva_venta.id_state = ArtState.objects.get(nombre="Inactive") # Pasamos la entrada a modo inactivo
            nueva_venta.save() # Hace que esa entrada pase a estar inactiva
        except TypeError:
            ctx['mensaje'] = 'Error. Uno o varios artículos no poseen porcentaje de ganancia. Agregalos en "Agregar o Modificar" Luego registra nuevamente la compra.'
            nueva_venta = Entrada.objects.get(id_state=estado)
            nueva_venta.delete() # Se borra el registro de la entrada que está activa, y los detalles se borran automaticamente al estar en modo CASCADE (models.py)


    except ObjectDoesNotExist as DoesNotExist:
        return redirect('not_found')


    return HttpResponse(template.render(ctx, request))

@login_required
def historial_compras(request):
    template = loader.get_template('historial_ventas.html')
    miFormulario = FormFiltroFecha()
    if Entrada.get_inactive().exists():

        ctx = {
            "datos_generales": stock_total(),
            "transaccion": Entrada.get_inactive(),
            "form": miFormulario,
            "titulo": "Historial de compras"
        }
        # Filtro fecha
        if request.method == "POST":
            miFormulario = FormFiltroFecha(request.POST)
            if miFormulario.is_valid():
                infForm = miFormulario.cleaned_data
                ctx["transaccion"] = Entrada.objects.filter(fecha__range=[infForm['fecha_inicial'], infForm['fecha_final']]).order_by('-fecha', '-id')
        else:
            miFormulario = FormFiltroFecha()
        # !filtro fecha

        return HttpResponse(template.render(ctx, request))

    else:
        return redirect('venta_exitosa')

@login_required
def detalle_entrada(request, id_entrada):
    try:
        return FileResponse(emitir_detalle_entrada(id_entrada), as_attachment=False, filename='hello.pdf')
    except ObjectDoesNotExist as DoesNotExist:
        return redirect('not_found')


# Funcion util para compra o venta
@login_required
def cancelar(request):
    template = loader.get_template('mensaje.html')
    estado = ArtState.objects.get(nombre="Active")
    try:
        nueva_venta = Entrada.objects.get(id_state=estado)
        nueva_venta.delete() # Se borra el registro de la entrada que está activa, y los detalles se borran automaticamente al estar en modo CASCADE (models.py)
    except ObjectDoesNotExist as DoesNotExist:
        try:
            nueva_venta = Venta.objects.get(id_state=estado)
            nueva_venta.delete()
        except ObjectDoesNotExist as DoesNotExist:
            return redirect('not_found')

    ctx = {'mensaje': 'Se ha cancelado la transacción.',
           'redireccion': 'Volviendo a la página de ventas...'}

    return HttpResponse(template.render(ctx, request))


# Funciones para administrar la mercadería
@login_required
def agregar_articulo(request):
    template = loader.get_template('agregar_modificar.html')
    miFormulario = FormNuevoArticulo()
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
                Article.objects.get(codigo=infForm['codigo'])
                ctx['mensaje'] = "El código ya está siendo utilizado por otro producto."
            except ObjectDoesNotExist as DoesNotExist:
                if infForm['costo'] is not None and infForm['costo_sin_iva'] is not None:
                    ctx['mensaje'] = "PROBLEMA: Los campos costo final y costo neto + IVA estan completados. Debes llenar solo uno de estos dos campos."
                elif infForm['costo'] is not None or infForm['costo_sin_iva'] is not None:
                    Article.objects.create(codigo=crear_articulo(infForm)['codigo'],
                                           descripcion=crear_articulo(infForm)['descripcion'],
                                           costo_sin_iva=crear_articulo(infForm)['costo_sin_iva'],
                                           costo=crear_articulo(infForm)['costo'],
                                           precio_sin_iva=crear_articulo(infForm)['precio_sin_iva'],
                                           precio=crear_articulo(infForm)['precio'],
                                           porcentaje_ganancia=crear_articulo(infForm)['porcentaje_ganancia'],
                                           porcentaje_descuento=crear_articulo(infForm)['porcentaje_descuento'],
                                           precio_descontado=crear_articulo(infForm)['precio_descontado'],
                                           seccion=crear_articulo(infForm)['seccion'],
                                           marca=crear_articulo(infForm)['marca'],
                                           modelo=crear_articulo(infForm)['modelo'],
                                           stock=crear_articulo(infForm)['stock'],
                                           alarma_stock=crear_articulo(infForm)['alarma_stock'])
                    return redirect('control_inventario')
                else:
                    ctx['mensaje'] = "PROBLEMA: Debes rellenar uno de los dos costos."
                ctx['datos_generales'] = stock_total() # Actualiza el stock cuando se hace la compra, asi no va atrasado
                miFormulario = FormNuevoArticulo()
    else:
        miFormulario = FormNuevoArticulo()
    return HttpResponse(template.render(ctx, request))

@login_required
def control_inventario(request):
    template = loader.get_template('control_inventario.html')
    miFormulario = FormBusqueda()
    ctx = {
        "datos_generales": stock_total(),
        "articulos": inventario(Article).order_by('descripcion'),
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

@login_required
def articulo(request, codigo_articulo):
    # Modificar un artículo existente.
    template = loader.get_template('agregar_modificar.html')
    try:
        new_article = Article.objects.get(codigo=codigo_articulo)
    except ObjectDoesNotExist as DoesNotExist:
        return redirect('not_found')
    else:
        detalles_formulario = {
            'codigo': new_article.codigo,
            'descripcion': new_article.descripcion,
            'costo': new_article.costo,
            'porcentaje_ganancia': new_article.porcentaje_ganancia,
            'porcentaje_descuento': new_article.porcentaje_descuento,
            'seccion': new_article.seccion,
            'marca': new_article.marca,
            'modelo': new_article.modelo,
            'stock': new_article.stock,
            'alarma_stock': new_article.alarma_stock
        }
        miFormulario = FormNuevoArticulo(detalles_formulario)
        ctx = {
            "datos_generales": stock_total(),
            "articulos": inventario(Article),
            "form": miFormulario,
            "titulo": "Modificar Artículo"
        }

        if request.method == "POST":
            miFormulario = FormNuevoArticulo(request.POST)
            if miFormulario.is_valid():
                infForm = miFormulario.cleaned_data

                if infForm['costo'] != None and infForm['costo_sin_iva'] != None:

                    ctx['mensaje'] = "PROBLEMA: Los campos costo final y costo neto + IVA estan completados. Debes llenar solo uno de estos dos campos."

                elif infForm['costo'] != None or infForm['costo_sin_iva'] != None:

                    new_article.codigo = infForm['codigo']
                    if infForm['descripcion'] != "":
                        new_article.descripcion = infForm['descripcion']
                    new_article.costo_sin_iva = infForm['costo_sin_iva']
                    new_article.costo = crear_articulo(infForm)['costo']
                    new_article.porcentaje_ganancia = infForm['porcentaje_ganancia']
                    new_article.precio_sin_iva = crear_articulo(infForm)['precio_sin_iva']
                    new_article.precio = crear_articulo(infForm)['precio']
                    new_article.porcentaje_descuento = crear_articulo(infForm)['porcentaje_descuento']
                    new_article.precio_descontado = crear_articulo(infForm)['precio_descontado']
                    if infForm['seccion'] != "":
                        new_article.seccion = infForm['seccion']
                    new_article.marca = infForm['marca']
                    new_article.modelo = infForm['modelo']
                    new_article.stock = infForm['stock']
                    new_article.alarma_stock = infForm['alarma_stock']
                    new_article.save() # Guardamos los cambios en la base de datos

                    return redirect('control_inventario')

                else:
                    ctx['mensaje'] = "PROBLEMA: Debes rellenar uno de los dos costos."
                    miFormulario = FormNuevoArticulo(detalles_formulario)

        else:
            miFormulario = FormNuevoArticulo(detalles_formulario)

    return HttpResponse(template.render(ctx, request))


# Funciones para administrar las ventas
@login_required
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
        "cliente": "",
        "descuento": venta_activa()[1].descuento,
        "total_con_descuento": venta_activa()[1].total_con_descuento
    }
    if venta_activa()[1].cliente != None:
        ctx['cliente'] = venta_activa()[1].cliente.nombre

    if request.method == "POST":
        miFormulario = FormVenta(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data # Sacamos los datos del formulario en un diccionario y lo metemos a una variable

            ##
            # Venta
            ##

            try: # Si ya hay un objeto activo, solo agregarle elementos de tipo detalle_Venta a su id
                nueva_venta = Venta.objects.get(id_state=estado)

            except ObjectDoesNotExist as DoesNotExist: # Si no hay ninguno activo, crearlo.
                nueva_venta = Venta.objects.create(fecha=date.today(),
                                                   total=0,
                                                   id_state=estado,
                                                   descuento=0,
                                                   cliente=buscar_cliente(infForm['dni_cliente'])) # Iniciar un objeto de tipo Venta (id(auto), fecha, id_state=1(active), total=0)
            else:
                if infForm['dni_cliente'] != None:
                    nueva_venta.cliente = buscar_cliente(infForm['dni_cliente'])

                elif infForm['cliente'] != None:
                    try:
                        nueva_venta.cliente = buscar_cliente(infForm['cliente'])
                    except:
                        nueva_venta.cliente = None
                        ctx['cliente'] = "Hay más de un cliente con el mismo nombre, probar con DNI."

                nueva_venta.save()

            ##
            # Articulo
            ##

            try: # Si el producto existe en la base de datos
                new_article = Article.objects.get(codigo=infForm['codigo']) # Llamamos al objeto desde la db que tenga el mismo codigo que en
                                                                            # el formulario y lo metemos como QuerySet en una variable.

                ##
                # Detalle de venta
                ##

                if new_article.stock >= infForm['cantidad']:
                    DetalleVenta.objects.create(costo_unitario=new_article.costo, # Iniciar un objeto de tipo detalle_venta
                                                precio_unitario=new_article.precio,
                                                porcentaje_descuento=new_article.porcentaje_descuento,
                                                descuento=new_article.precio * new_article.porcentaje_descuento / 100,
                                                cantidad=infForm['cantidad'],
                                                id_venta=Venta.objects.get(id_state=estado),
                                                id_producto=Article.objects.get(codigo=infForm['codigo']))
                else:
                    ctx['inexistente'] = 'No hay suficiente stock del producto.'

            except ObjectDoesNotExist as DoesNotExist: # Si el producto no existe en la base de datos
                ctx['inexistente'] = 'Artículo inexistente, debe agregarlo en la sección "Control de inventario/Agregar artículo". El resto de la venta seguirá guardada.'

            # Se suman los precios unitarios al precio total de la venta
            lista = DetalleVenta.objects.filter(id_venta=nueva_venta)
            nueva_venta.total = 0
            nueva_venta.descuento = 0
            for i in lista:
                nueva_venta.total += (i.precio_unitario * i.cantidad)
                if i.descuento != None:
                    nueva_venta.descuento += (i.descuento * i.cantidad)
            nueva_venta.total_con_descuento = nueva_venta.total - nueva_venta.descuento

            nueva_venta.save()
            ctx['total'] = nueva_venta.total
            ctx['descuento'] = nueva_venta.descuento
            ctx['total_con_descuento'] = nueva_venta.total_con_descuento
            ctx['articulo_a_vender'] = lista
            miFormulario = FormVenta({'cantidad': 1, 'dni_cliente': dni_cliente()})
            ctx['form'] = miFormulario
            if nueva_venta.cliente != None:
                ctx['cliente'] = nueva_venta.cliente.nombre

            return HttpResponse(template.render(ctx, request))
    else:
        # Es es formulario que se muestra antes de enviar la info. La cantidad por defecto de articulos a vender es 1.
        miFormulario = FormVenta({'cantidad': 1, 'dni_cliente': dni_cliente()})

    return HttpResponse(template.render(ctx, request))

@login_required
def historial_ventas(request):
    template = loader.get_template('historial_ventas.html')
    miFormulario = FormFiltroFecha()
    if Venta.get_inactive().exists():
        ctx = {
            "datos_generales": stock_total(),
            "transaccion": Venta.get_inactive(),
            "form": miFormulario,
            "titulo": "Historial de ventas"
        }
        # Filtro fecha
        if request.method == "POST":
            miFormulario = FormFiltroFecha(request.POST)
            if miFormulario.is_valid():
                infForm = miFormulario.cleaned_data
                ctx["transaccion"] = Venta.objects.filter(fecha__range=[infForm['fecha_inicial'], infForm['fecha_final']]).order_by('-fecha', '-id')
        else:
            miFormulario = FormFiltroFecha()
        # !filtro fecha

        return HttpResponse(template.render(ctx, request))

    else:
        return redirect('venta_exitosa')

class DetalleDeVenta(ListView):
    model = DetalleVenta


@login_required
def recibo(request, id_venta):
    try:
        return FileResponse(emitir_recibo(id_venta), as_attachment=False, filename='hello.pdf')
    except ObjectDoesNotExist as DoesNotExist:
        return redirect('not_found')

@login_required
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
            return redirect('not_found')
        ctx['id_venta'] = nueva_venta.id
    except ObjectDoesNotExist as DoesNotExist:
        return redirect('not_found')


    return HttpResponse(template.render(ctx, request))

@login_required
def cancelar_unidad(request, codigo_articulo):
    try:
        articulo_staging = DetalleVenta.objects.get(id=codigo_articulo)
    except ObjectDoesNotExist as DoesNotExist:
        pass
    else:
        articulo_staging.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER')) # esto hace que se redirija a la url anterior.


# Funcion que debe ejecutarse en la instalacion del programa
@login_required
def script_actualizacion(request):
    template = loader.get_template('mje_sin_redireccion.html')
    ctx = {'titulo': 'Se agregaron los nuevos valores',
           'mensaje': 'Checkear en DB...'}
    '''campos_sin_iva()
    if not ArtState.objects.all().exists():
        add_art_state()'''
    '''
    articulos = Article.objects.all()
    for i in articulos:
        i.porcentaje_descuento = 0
        i.precio_descontado = 0
        i.save()
    '''

    return HttpResponse(template.render(ctx, request))


#Funciones para administrar los clientes
@login_required
def cliente(request):
    template = loader.get_template('agregar_modificar.html')
    miFormulario = FormCliente()
    lista = []
    ctx = {
        "articulo_a_vender": lista,
        "datos_generales": stock_total(),
        "form": miFormulario,
        "mensaje": "",
        "titulo": "Añadir cliente"
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
                                                    condicion_iva=infForm['condicion_iva'],
                                                    dni=infForm['dni'],
                                                    cuit=infForm['cuit'],
                                                    direccion=infForm['direccion'],
                                                    telefono=infForm['telefono'],
                                                    email=infForm['email'])

                return redirect('control_clientes')

            miFormulario = FormCliente()

    return HttpResponse(template.render(ctx, request))

@login_required
def control_clientes(request):
    template = loader.get_template('control_personas.html')
    miFormulario = FormBusqueda()
    ctx = {
        "titulo": "Clientes",
        "datos_generales": stock_total(),
        "articulos": inventario(Cliente).order_by('nombre'),
        "agregar_persona": "+ Agregar Cliente",
        "link_agregar": "/cliente",
        "link_modificar": "/modificar_cliente/",
        "form": miFormulario
    }

    if request.method == "POST":
        miFormulario = FormBusqueda(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data
            resultado = Cliente.objects.filter(dni=int(infForm['buscar'])) # Código
            ctx["articulos"] = resultado
    else:
        miFormulario = FormBusqueda()

    return HttpResponse(template.render(ctx, request))

@login_required
def modificar_cliente(request, id_param):
    template = loader.get_template('agregar_modificar.html')
    try:
        new_cliente = Cliente.objects.get(id=id_param)
    except ObjectDoesNotExist as DoesNotExist:
        return redirect('not_found')
    else:
        detalles_formulario = {
            'nombre': new_cliente.nombre,
            'condicion_iva': new_cliente.condicion_iva,
            'dni': new_cliente.dni,
            'cuit': new_cliente.cuit,
            'direccion': new_cliente.direccion,
            'telefono': new_cliente.telefono,
            'email': new_cliente.email
        }
        miFormulario = FormCliente(detalles_formulario)
        ctx = {
            "datos_generales": stock_total(),
            "articulos": inventario(Cliente),
            "form": miFormulario,
            "mensaje": "",
            "titulo": "Modificar cliente"
        }

        if request.method == "POST":
            miFormulario = FormCliente(request.POST)
            if miFormulario.is_valid():
                infForm = miFormulario.cleaned_data # Sacamos los datos del formulario en un diccionario y lo metemos a una variable

                new_cliente.nombre = infForm["nombre"]
                new_cliente.condicion_iva = infForm["condicion_iva"]
                new_cliente.dni = infForm["dni"]
                new_cliente.cuit = infForm["cuit"]
                new_cliente.direccion = infForm["direccion"]
                new_cliente.telefono = infForm["telefono"]
                new_cliente.email = infForm["email"]

                new_cliente.save()

                return redirect('control_clientes')

        return HttpResponse(template.render(ctx, request))


#Funciones para administrar los proveedores
@login_required
def proveedor(request):
    template = loader.get_template('agregar_modificar.html')
    miFormulario = FormProveedor()
    lista = []
    ctx = {
        "articulo_a_vender": lista,
        "datos_generales": stock_total(),
        "form": miFormulario,
        "mensaje": "",
        "titulo": "Añadir proveedor"
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

@login_required
def modificar_proveedor(request, id_param):
    template = loader.get_template('agregar_modificar.html')
    try:
        new_proveedor = Proveedor.objects.get(id=id_param)
    except ObjectDoesNotExist as DoesNotExist:
        return redirect('not_found')
    else:
        detalles_formulario = {
            'nombre': new_proveedor.nombre,
            'condicion_iva': new_proveedor.condicion_iva,
            'cuit': new_proveedor.cuit,
            'direccion': new_proveedor.direccion,
            'telefono': new_proveedor.telefono,
            'email': new_proveedor.email
        }
        miFormulario = FormProveedor(detalles_formulario)
        ctx = {
            "datos_generales": stock_total(),
            "articulos": inventario(Proveedor),
            "form": miFormulario,
            "mensaje": "",
            "titulo": "Modificar proveedor"
        }

        if request.method == "POST":
            miFormulario = FormProveedor(request.POST)
            if miFormulario.is_valid():
                # Sacamos los datos del formulario en un diccionario y lo metemos a una variable
                infForm = miFormulario.cleaned_data

                new_proveedor.nombre = infForm["nombre"]
                new_proveedor.condicion_iva = infForm["condicion_iva"]
                new_proveedor.cuit = infForm["cuit"]
                new_proveedor.direccion = infForm["direccion"]
                new_proveedor.telefono = infForm["telefono"]
                new_proveedor.email = infForm["email"]

                new_proveedor.save()

                return redirect('control_clientes')

        return HttpResponse(template.render(ctx, request))

@login_required
def control_proveedores(request):
    template = loader.get_template('control_personas.html')
    ctx = {
        "titulo": "Proveedores",
        "datos_generales": stock_total(),
        "articulos": inventario(Proveedor).order_by('nombre'),
        "agregar_persona": "+ Agregar Proveedor",
        "link_agregar": "/proveedor",
        "link_modificar": "/modificar_proveedor/"
    }

    return HttpResponse(template.render(ctx, request))

@login_required
def not_found(request):
    template = loader.get_template('error_404.html')
    ctx = {"titulo": "Error 404. Su solicitud no fue encontrada."}
    return HttpResponse(template.render(ctx, request))

@login_required
def error_404(request, exception):
    template = loader.get_template('error/404.html')
    ctx = {"titulo": "Error 404."}
    return HttpResponse(template.render(ctx, request))
