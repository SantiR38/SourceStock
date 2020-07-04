from django.shortcuts import render
from django.http import HttpResponse
from django.template import Template, Context, loader
from django.core.exceptions import ObjectDoesNotExist, FieldError
from erp.forms import FormVenta, FormNuevoArticulo, FormEntrada, FormCliente
from erp.models import Article, ArtState, Entrada, DetalleEntrada, Venta, DetalleVenta, Perdida, DetallePerdida
from erp.functions import stock_total, porcentaje_ganancia, inventario
from datetime import date

def index(request):
    template = loader.get_template('index.html')
    miFormulario = FormVenta({'cantidad': 1})
    lista = []
    ctx = {
        "articulo_a_vender": lista,
        "datos_generales": stock_total(),
        "form": miFormulario
    }
    # Manejo del formulario de venta
    if request.method == "POST":
        miFormulario = FormVenta(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data # Sacamos los datos del formulario en un diccionario y lo metemos a una variable
            try: # Si el producto existe en la base de datos
                new_article = Article.objects.get(codigo=infForm['codigo']) # Llamamos al objeto desde la db que tenga el mismo codigo que en el formulario
                                                                            # y lo metemos como QuerySet en una variable.
                if new_article.stock >= infForm['cantidad']:
                    new_article.stock -= infForm['cantidad'] # Actualizamos el stock disponible
                    new_article.save() # Guardamos los cambios de la linea anterior en la base de datos
                    ctx['stock_insuficiente'] = ""
                else:
                    ctx['stock_insuficiente'] = "No existe esa cantidad de articulos disponibles"
                lista.append(new_article) # Colocamos el QuerySet anterior en una lista que esta en el contexto (ctx)

                ctx['datos_generales'] = stock_total() # Actualiza el stock cuando se hace la venta, asi no va atrasado
                ctx['inexistente'] = ''
            except ObjectDoesNotExist as DoesNotExist: # Si el producto no existe en la base de datos
                ctx['inexistente'] = 'Artículo inexistente'

            miFormulario = FormVenta({'cantidad': 1})
            return HttpResponse(template.render(ctx, request))
    else:
        # Es es formulario que se muestra antes de enviar la info. La cantidad por defecto de articulos a vender es 1.
        miFormulario = FormVenta({'cantidad': 1})

    return HttpResponse(template.render(ctx, request))


def agregar_modificar(request):
    template = loader.get_template('agregar_modificar.html')
    miFormulario = FormNuevoArticulo()
    lista = []
    ctx = {
        "articulo_a_agregar": lista, 
        "datos_generales": stock_total(),
        "form": miFormulario,
    }
    # Manejo del formulario de compra
    if request.method == "POST":
        miFormulario = FormNuevoArticulo(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data
            try:
                new_article = Article.objects.get(codigo=infForm['codigo'])
                ctx['mensaje_error'] = "El código ya está siendo utilizado por otro producto."
            except ObjectDoesNotExist as DoesNotExist:
                new_article = Article.objects.create(codigo=infForm['codigo'],
                                                    descripcion=infForm['descripcion'],
                                                    precio=porcentaje_ganancia(infForm['costo'], infForm['porcentaje_ganancia']),
                                                    porcentaje_ganancia=infForm['porcentaje_ganancia'],
                                                    costo=infForm['costo'],
                                                    seccion=infForm['seccion'],
                                                    stock=infForm['stock'])
                ctx['datos_generales'] = stock_total() # Actualiza el stock cuando se hace la compra, asi no va atrasado

                lista.append(new_article) # Colocamos el QuerySet anterior en una lista que esta en el contexto (ctx)
            miFormulario = FormNuevoArticulo()

            return HttpResponse(template.render(ctx, request))
    else:
        miFormulario = FormNuevoArticulo()

    return HttpResponse(template.render(ctx, request))


def compra_simple(request):
    template = loader.get_template('compra_simple.html')
    miFormulario = FormVenta({'cantidad': 1})
    lista = []
    ctx = {
        "articulo_a_comprar": lista,
        "datos_generales": stock_total(),
        "form": miFormulario
    }
    # Manejo del formulario de compra simple
    if request.method == "POST":
        miFormulario = FormVenta(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data # Sacamos los datos del formulario en un diccionario y lo metemos a una variable
            try: # Si el producto existe en la base de datos
                new_article = Article.objects.get(codigo=infForm['codigo']) # Llamamos al objeto desde la db que tenga el mismo codigo que en
                                                                            # el formulario y lo metemos como QuerySet en una variable.

                new_article.stock += infForm['cantidad'] # Actualizamos el stock disponible
                new_article.save() # Guardamos los cambios de la linea anterior en la base de datos

                lista.append(new_article) # Colocamos el QuerySet anterior en una lista que esta en el contexto (ctx)

                ctx['datos_generales'] = stock_total() # Actualiza el stock cuando se hace la compra, asi no va atrasado
                ctx['inexistente'] = ''
            except ObjectDoesNotExist as DoesNotExist: # Si el producto no existe en la base de datos
                ctx['inexistente'] = 'Artículo inexistente, debe agregarlo en la pestaña "Agregar artículo"'

            miFormulario = FormVenta({'cantidad': 1})
            
            return HttpResponse(template.render(ctx, request))
    else:
        # Es es formulario que se muestra antes de enviar la info. La cantidad por defecto de articulos a comprar es 1.
        miFormulario = FormVenta({'cantidad': 1})

    return HttpResponse(template.render(ctx, request))


def entrada(request):
    template = loader.get_template('entrada.html')
    miFormulario = FormEntrada({'cantidad': 1, 'fecha':date.today()})
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
            try: # Si el producto existe en la base de datos
                new_article = Article.objects.get(codigo=infForm['codigo']) # Llamamos al objeto desde la db que tenga el mismo codigo que en
                                                                            # el formulario y lo metemos como QuerySet en una variable.
                if new_article.porcentaje_ganancia == None:
                    ctx["porcentaje_inexistente"] = "Este producto no tiene porcentaje de ganancia. Agrégalo en la sección 'Agregar o modificar' antes de continuar."
                try: # Si ya hay un objeto activo, solo agregarle elementos de tipo detalle_entrada a su id
                    nueva_venta = Entrada.objects.get(id_state=estado)
                except ObjectDoesNotExist as DoesNotExist:
                    nueva_venta = Entrada.objects.create(fecha=infForm['fecha'],
                                                         total=0,
                                                         id_state=estado) # Iniciar un objeto de tipo entrada (id(auto), fecha, id_state=1(active), total=0)

                
                producto_leido = DetalleEntrada.objects.create(costo_unitario=infForm['costo'], # Iniciar un objeto de tipo detalle_entrada
                                                               cantidad=infForm['cantidad'],
                                                               id_entrada=Entrada.objects.get(id_state=estado),
                                                               id_producto=Article.objects.get(codigo=infForm['codigo']))
            # Se suman los precios unitarios al precio total de la compra
                lista = DetalleEntrada.objects.filter(id_entrada = nueva_venta) 
                nueva_venta.total = 0
                for i in lista:
                    nueva_venta.total += (i.costo_unitario * i.cantidad)
                nueva_venta.save()
                ctx['total'] = nueva_venta.total


                '''
                ctx['datos_generales'] = stock_total() # Actualiza el stock cuando se hace la compra, asi no va atrasado
                '''
                ctx['inexistente'] = ''
                ctx['articulo_a_comprar'] = lista
            except ObjectDoesNotExist as DoesNotExist: # Si el producto no existe en la base de datos
                ctx['inexistente'] = 'Artículo inexistente, debe agregarlo en la pestaña "Agregar artículo". El resto de la compra seguirá guardada.'

            miFormulario = FormEntrada({'cantidad': 1, 'fecha':date.today()})
            
            return HttpResponse(template.render(ctx, request))
    else:
        # Es es formulario que se muestra antes de enviar la info. La cantidad por defecto de articulos a comprar es 1.
        miFormulario = FormEntrada({'cantidad': 1, 'fecha':date.today()})

    return HttpResponse(template.render(ctx, request))


def venta(request):
    template = loader.get_template('venta.html')
    miFormulario = FormVenta({'cantidad': 1})
    lista = []
    ctx = {
        "articulo_a_vender": lista,
        "datos_generales": stock_total(),
        "form": miFormulario,
        "total": 0
    }
    if request.method == "POST":
        miFormulario = FormVenta(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data # Sacamos los datos del formulario en un diccionario y lo metemos a una variable
            estado = ArtState.objects.get(nombre="Active") # Creamos un ArtState instance para definir una transacción Activa
            try: # Si el producto existe en la base de datos
                new_article = Article.objects.get(codigo=infForm['codigo']) # Llamamos al objeto desde la db que tenga el mismo codigo que en
                                                                            # el formulario y lo metemos como QuerySet en una variable.
                try: # Si ya hay un objeto activo, solo agregarle elementos de tipo detalle_Venta a su id
                    nueva_venta = Venta.objects.get(id_state=estado)
                except ObjectDoesNotExist as DoesNotExist: # Si no hay ninguno activo, crearlo.
                    nueva_venta = Venta.objects.create(fecha=date.today(),
                                                         total=0,
                                                         id_state=estado) # Iniciar un objeto de tipo Venta (id(auto), fecha, id_state=1(active), total=0)

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

            miFormulario = FormVenta({'cantidad': 1 })
            
            return HttpResponse(template.render(ctx, request))
    else:
        # Es es formulario que se muestra antes de enviar la info. La cantidad por defecto de articulos a vender es 1.
        miFormulario = FormVenta({'cantidad': 1})

    return HttpResponse(template.render(ctx, request))


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
                i.id_producto.costo = i.costo_unitario
                i.id_producto.precio = i.costo_unitario + (i.costo_unitario * i.id_producto.porcentaje_ganancia / 100)
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
    template = loader.get_template('entrada.html')
    miFormulario = FormCliente()
    lista = []
    ctx = {
        "articulo_a_vender": lista,
        "datos_generales": stock_total(),
        "form": miFormulario
    }

    return HttpResponse(template.render(ctx, request))


def control_inventario(request):
    template = loader.get_template('control_inventario.html')
    ctx = {
        "datos_generales": stock_total(),
        "articulos": inventario()
    }

    return HttpResponse(template.render(ctx, request))

def articulo(request, codigo_articulo):
    template = loader.get_template('agregar_modificar.html')
    new_article = Article.objects.get(codigo=codigo_articulo)
    detalles_formulario = {
        'codigo': new_article.codigo,
        'descripcion': new_article.descripcion,
        'costo': new_article.costo,
        'porcentaje_ganancia': new_article.porcentaje_ganancia,
        'seccion': new_article.seccion,
        'stock': new_article.stock
    }
    miFormulario = FormNuevoArticulo(detalles_formulario)
    lista = []
    ctx = {
        "datos_generales": stock_total(),
        "articulos": inventario(),
        "form": miFormulario,
    }
    
    if request.method == "POST":
        miFormulario = FormNuevoArticulo(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data
            
            new_article.codigo = infForm['codigo']
            if infForm['descripcion'] != "":
                new_article.descripcion = infForm['descripcion']
            new_article.costo = infForm['costo']
            new_article.porcentaje_ganancia = infForm['porcentaje_ganancia']
            new_article.precio = porcentaje_ganancia(infForm['costo'], infForm['porcentaje_ganancia']) # costo+(costo*porcentaje/100)
            if infForm['seccion'] != "":
                new_article.seccion = infForm['seccion']
            new_article.stock = infForm['stock']
            new_article.save() # Guardamos los cambios de la linea anterior en la base de datos
            ctx['datos_generales'] = stock_total() # Actualiza el stock cuando se hace la compra, asi no va atrasado

            lista.append(new_article) # Colocamos el QuerySet anterior en una lista que esta en el contexto (ctx)
            miFormulario = FormNuevoArticulo()

            return HttpResponse(template.render(ctx, request))
    else:
        miFormulario = FormNuevoArticulo(detalles_formulario)

    return HttpResponse(template.render(ctx, request))