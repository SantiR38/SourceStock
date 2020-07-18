from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.template import Template, Context, loader
from django.core.exceptions import ObjectDoesNotExist, FieldError
from erp.forms import FormVenta, FormNuevoArticulo, FormEntrada, FormCliente, FormBusqueda
from erp.models import Article, ArtState, Entrada, DetalleEntrada, Venta, DetalleVenta, Perdida, DetallePerdida, Cliente
from erp.functions import stock_total, porcentaje_ganancia, inventario, venta_activa, buscar_cliente, dni_cliente, campos_sin_iva, precio_final
from reportlab.pdfgen import canvas
from datetime import date
from decimal import *
import io

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
    miFormulario = FormEntrada({'cantidad': 1})
    lista = []
    ctx = {
        "articulo_a_comprar": lista,
        "datos_generales": stock_total(),
        "form": miFormulario,
        "total": 0,
        "porcentaje_inexistente": ""
    }

    if request.method == "POST":
        miFormulario = FormEntrada(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data # Sacamos los datos del formulario en un diccionario y lo metemos a una variable
            estado = ArtState.objects.get(nombre="Active") # Creamos un ArtState instance para definir una transacción Activa
            
            try: # Si ya hay un objeto activo, solo agregarle elementos de tipo detalle_entrada a su id
                    nueva_venta = Entrada.objects.get(id_state=estado)
            except ObjectDoesNotExist as DoesNotExist:
                nueva_venta = Entrada.objects.create(fecha=infForm['fecha'],
                                                        total=0,
                                                        id_state=estado) # Iniciar un objeto de tipo entrada (id(auto), fecha, id_state=1(active), total=0)

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
                ctx['inexistente'] = 'Artículo inexistente, debe agregarlo en la pestaña "Agregar artículo". El resto de la compra seguirá guardada.'
            
            lista = DetalleEntrada.objects.filter(id_entrada = nueva_venta) 
            nueva_venta.total = 0
            for i in lista:
                nueva_venta.total += (i.costo_unitario * i.cantidad)
            nueva_venta.save()
            ctx['total'] = nueva_venta.total
            ctx['articulo_a_comprar'] = lista

            miFormulario = FormEntrada({'cantidad': 1})
            
            return HttpResponse(template.render(ctx, request))
    else:
        # Es es formulario que se muestra antes de enviar la info. La cantidad por defecto de articulos a comprar es 1.
        miFormulario = FormEntrada({'cantidad': 1})

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
                ctx['inexistente'] = 'Artículo inexistente, debe agregarlo en la pestaña "Agregar artículo". El resto de la venta seguirá guardada.'

            miFormulario = FormVenta({'cantidad': 1, 'dni_cliente': dni_cliente()})
            ctx['form'] = miFormulario
            if nueva_venta.cliente != None:
                ctx['cliente'] = nueva_venta.cliente.nombre + " " + nueva_venta.cliente.apellido
            
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
           'redireccion': 'Volviendo a la página de ventas...'}

    estado = ArtState.objects.get(nombre="Active")
    try:
        nueva_venta = Venta.objects.get(id_state=estado)

        producto_leido = DetalleVenta.objects.filter(id_venta=nueva_venta) # Se crea un QuerySet para sacar datos de cada producto comprado

        for i in producto_leido: # Se actualiza  el stock de cada objeto Article
            i.id_producto.stock -= i.cantidad
            i.id_producto.save()
        
        nueva_venta.id_state = ArtState.objects.get(nombre="Inactive") # Pasamos la entrada a modo inactivo
        nueva_venta.save() # Hace que esa entrada pase a estar inactiva
    except ObjectDoesNotExist as DoesNotExist:
        ctx['mensaje'] = 'Error 404. Tu solicitud no fue encontrada.'
    
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
    pass


def recibo(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.setFont("Helvetica", 26)
    p.drawString(327, 790, "Recibo") #(Ancho, Alto, "Texto")
    p.setFont("Helvetica", 10)
    p.drawString(328, 770, "Documento no válido como factura")
    p.drawString(328, 740, "Fecha de emisión:")
    p.drawString(328, 710, "Responsable Inscripto")
    p.drawString(462, 710, "CUIT: 20-32987598-4")

    p.drawString(38, 693, "Dir: Av. Amadeo Sabattini 2917, Río Cuarto (Cba.)")
    p.drawString(297.5, 693, "Tel: 358 517-0913")
    p.drawString(420, 693, "Inicio Actividad: 01/01/2020")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(80, 710, "LA CASA DE LAS BATERÍAS")

    p.setFont("Helvetica-Bold", 10)
    p.drawString(38, 673, "Cliente: ")
    p.drawString(38, 653, "Dirección: ")
    p.drawString(297.5, 673, "Cond. IVA: ")
    p.drawString(297.5, 653, "CUIT: ")

    p.setFont("Helvetica", 10)
    p.drawString(95, 673, "Juan Perez")
    p.drawString(95, 653, "Belgrano 1110")
    p.drawString(355, 673, "Consumidor Final")
    p.drawString(355, 653, "20-35867843-8")

    # Header
    p.line(30, 820, 565, 820) #Horizontal Grande
    p.line(30, 690, 565, 690) #Horizontal Grande
    p.line(30, 820, 30, 690) #Vertical Izq
    p.line(565, 820, 565, 690) #Vertical Der
    p.line(30, 705, 565, 705) #Horizontal Grande
    p.line(297.5, 785, 297.5, 705) #Vertical medio
    p.line(318, 785, 318, 820) #Vertical
    p.line(277, 785, 277, 820) #Vertical
    p.line(277, 785, 318, 785)

    p.setFont("Helvetica", 30)
    p.drawString(288, 790, "X")




    #Titulos de tabla
    alto = 600
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, alto, "Cantidad")
    p.drawString(150, alto, "Detalles")
    p.drawString(390, alto, "P. Unitario")
    p.drawString(490, alto, "P. Total")
    p.line(50, 590, 535, 590)

    # Articulos a vender (va a ser con bucle for)
    alto = 550
    p.setFont("Helvetica", 11)

    p.drawString(50, alto, "2")
    p.drawString(150, alto, "Batería Moura 70")
    p.drawString(390, alto, "5000")
    p.drawString(490, alto, "10000")

    alto -= 30

    p.drawString(50, alto, "1")
    p.drawString(150, alto, "Aromatizante para auto")
    p.drawString(390, alto, "300")
    p.drawString(490, alto, "300")

    # Filas total

    alto -= 50
    p.setFont("Helvetica-Bold", 11)
    p.drawString(390, alto, "Total")
    p.drawString(490, alto, "10300")


    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')

def script_actualizacion(request):
    template = loader.get_template('mje_sin_redireccion.html')
    ctx = {'titulo': 'Se agregaron los nuevos valores',
           'mensaje': 'Checkear en DB...'}
    campos_sin_iva()


    return HttpResponse(template.render(ctx, request))