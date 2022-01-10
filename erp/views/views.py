from datetime import date

from django.shortcuts import redirect
from django.http import HttpResponse, FileResponse, HttpResponseRedirect
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from api.models import PrecioDolar
from erp.forms import (FormVenta, FormNuevoArticulo, FormEntrada, FormCliente,
    FormBusqueda, FormFiltroFecha, FormProveedor)
from erp.models import (Article, ArtState, Entrada, DetalleEntrada, Venta,
    DetalleVenta, Cliente, Proveedor)
from erp.functions import (porcentaje_ganancia, venta_activa, compra_activa,
    buscar_cliente, comprar_articulo, buscar_proveedor, dni_cliente,
    emitir_recibo, nombre_proveedor, emitir_detalle_entrada)


@login_required
def entrada(request):
    template = loader.get_template('entrada.html')
    view_form = FormEntrada(
        {'cantidad': 1, 'proveedor': nombre_proveedor()})
    article_status = ArtState.objects.get(nombre="Active")
    ctx = {
        "articulo_a_comprar": compra_activa()[0],
        "form": view_form,
        "titulo": "Compra",
        "total": compra_activa()[1].total,
        "porcentaje_inexistente": "",
        "proveedor": ""
    }
    if compra_activa()[1].proveedor is not None:
        ctx['proveedor'] = compra_activa()[1].proveedor.nombre

    if request.method == "POST":
        view_form = FormEntrada(request.POST)
        if view_form.is_valid():
            # Sacamos los datos del formulario en un diccionario y lo metemos a una variable
            cleaned_form = view_form.cleaned_data
            # Si ya hay un objeto activo, solo agregarle
            # elementos de tipo detalle_entrada a su id
            new_sale = Entrada.objects.filter(id_state=article_status).first()
            if new_sale is None:
                new_sale = Entrada.objects.create(fecha=cleaned_form['fecha'],
                    total=0, id_state=article_status)
            new_sale.proveedor = buscar_proveedor(cleaned_form['proveedor'])
            new_sale.save()

            new_article = Article.objects.filter(
                codigo=cleaned_form['codigo']).first()
            if new_article is None:
                ctx['inexistente'] = ('Artículo inexistente, debe agregarlo en'
                    'la sección "Control de inventario/Agregar artículo". El '
                    'resto de la compra seguirá guardada.')
            elif new_article.porcentaje_ganancia is None:
                ctx["porcentaje_inexistente"] = ("Este producto no tiene "
                    "porcentaje de ganancia. Agrégalo en la sección "
                    "'Agregar o modificar' antes de continuar.")
            else:
                if cleaned_form.get('inexistente') is None:
                    DetalleEntrada.objects.create(costo_sin_iva=comprar_articulo(cleaned_form)['costo_sin_iva'],
                        costo_unitario=comprar_articulo(cleaned_form)['costo'],
                        costo_por_cantidad=comprar_articulo(cleaned_form)['costo'] * comprar_articulo(cleaned_form)['cantidad'],
                        cantidad=comprar_articulo(cleaned_form)['cantidad'],
                        id_entrada=new_sale,
                        en_dolar=comprar_articulo(cleaned_form)['en_dolar'],
                        id_producto=new_article)
                    ctx['inexistente'] = ''

            queryset = DetalleEntrada.objects.filter(id_entrada=new_sale)
            new_sale.total = 0
            for i in queryset:
                if i.en_dolar:
                    new_sale.total += (i.costo_unitario * i.cantidad * PrecioDolar.cotizacion_venta())
                else:
                    new_sale.total += (i.costo_unitario * i.cantidad)  # Se suman los precios unitarios al precio total de la compra
            new_sale.save()
            ctx['total'] = new_sale.total
            ctx['articulo_a_comprar'] = queryset

            view_form = FormEntrada({'cantidad': 1, 'proveedor': nombre_proveedor()})

            if compra_activa()[1].proveedor is not None:
                ctx['proveedor'] = compra_activa()[1].proveedor.nombre
            return HttpResponse(template.render(ctx, request))
    else:
        # Es es formulario que se muestra antes de enviar la info. La cantidad por defecto de articulos a comprar es 1.
        view_form = FormEntrada({'cantidad': 1, 'proveedor': nombre_proveedor()})

    return HttpResponse(template.render(ctx, request))


@login_required
def transaccion_exitosa(request):
    template = loader.get_template('mensaje.html')
    ctx = {'mensaje': 'Su transacción fue un éxito.',
           'titulo': 'Transacción exitosa',
           'redireccion': 'Volviendo a la página de ventas...'}

    article_status = ArtState.objects.get(nombre="Active")
    nueva_venta = Entrada.objects.filter(id_state=article_status).first()
    if nueva_venta is None:
        return redirect('not_found')

    producto_leido = DetalleEntrada.objects.filter(
        id_entrada=nueva_venta).select_related('id_producto')

    try:
        for j in producto_leido:  # Esto es simplemente para que cancele la compra completa y no se actualicen el stock y precio solo de algunos productos
            j.id_producto.porcentaje_ganancia * 1  # Es una multiplicacion que solo sirve para poner en evidencia el error (porque un numero no se puede multiplicar por 'None')
        for i in producto_leido:  # Se actualiza el costo y el stock de cada objeto Article
            i.id_producto.en_dolar = i.en_dolar
            i.id_producto.costo_sin_iva = i.costo_sin_iva
            i.id_producto.costo = i.costo_unitario
            i.id_producto.precio_sin_iva = porcentaje_ganancia(i.costo_sin_iva, i.id_producto.porcentaje_ganancia)
            i.id_producto.precio = porcentaje_ganancia(i.costo_unitario, i.id_producto.porcentaje_ganancia)
            i.id_producto.precio_descontado = porcentaje_ganancia(i.id_producto.precio, -i.id_producto.porcentaje_descuento)
            i.id_producto.stock += i.cantidad
            i.id_producto.save()

        nueva_venta.id_state = ArtState.objects.get(nombre="Inactive")  # Pasamos la entrada a modo inactivo
        nueva_venta.save()  # Hace que esa entrada pase a estar inactiva
    except TypeError:
        ctx['mensaje'] = ('Error. Uno o varios artículos no poseen porcentaje '
            'de ganancia. Agregalos en "Agregar o Modificar" Luego registra '
            'nuevamente la compra.')
        nueva_venta = Entrada.objects.get(id_state=article_status)
        nueva_venta.delete()  # Deletes sale_details in cascade

    return HttpResponse(template.render(ctx, request))

@login_required
def historial_compras(request):
    template = loader.get_template('historial_ventas.html')
    view_form = FormFiltroFecha()

    if not Entrada.get_inactive().exists():
        return redirect('venta_exitosa')
    
    ctx = {
        "transaccion": Entrada.get_inactive(),
        "form": view_form,
        "titulo": "Historial de compras"
    }
    # Filtro fecha
    if request.method == "POST":
        view_form = FormFiltroFecha(request.POST)
        if view_form.is_valid():
            cleaned_form = view_form.cleaned_data
            ctx["transaccion"] = Entrada.objects.filter(
                fecha__range=[cleaned_form['fecha_inicial'], cleaned_form['fecha_final']]
            ).order_by('-fecha', '-id')
    else:
        view_form = FormFiltroFecha()

    return HttpResponse(template.render(ctx, request))
        

@login_required
def detalle_entrada(request, id_entrada):
    purchase = Entrada.objects.filter(id=id_entrada).first()
    if purchase is None:
        return redirect('not_found')

    return FileResponse(emitir_detalle_entrada(id_entrada),
        as_attachment=False, filename=f'detalle_entrada_{purchase.fecha}.pdf')


@login_required
def cancelar(request):
    """
    Cancel transacciont view.
    ---
    Delete all the instances `Entrada` and `Venta` with `ArtState="Active"`.
    Useful only for sales and purchases.
    """
    template = loader.get_template('mensaje.html')
    state = ArtState.objects.get(nombre="Active")
    Entrada.objects.filter(id_state=state).delete()
    Venta.objects.filter(id_state=state).delete()

    ctx = {'mensaje': 'Se ha cancelado la transacción.',
        'titulo': 'Transacción cancelada',
        'redireccion': 'Volviendo a la página de ventas...'}

    return HttpResponse(template.render(ctx, request))


@login_required
def agregar_articulo(request):
    """Manage stock view."""
    template = loader.get_template('agregar_modificar.html')
    view_form = FormNuevoArticulo()
    ctx = {
        "form": view_form,
        "titulo": "Agregar artículo"
    }
    # Manejo del formulario de compra
    if request.method == "POST":
        view_form = FormNuevoArticulo(request.POST)
        if view_form.is_valid():
            ctx['mensaje'] = Article.create_new(view_form.cleaned_data)
            view_form = FormNuevoArticulo()
    else:
        view_form = FormNuevoArticulo()
    return HttpResponse(template.render(ctx, request))


@login_required
def control_inventario(request):
    template = loader.get_template('control_inventario.html')
    view_form = FormBusqueda()
    ctx = {
        "articulos": Article.objects.filter(id__lte=50).order_by('descripcion'),
        "form": view_form,
        "titulo": "Control de inventario"
    }

    if request.method == "POST":
        view_form = FormBusqueda(request.POST)
        if view_form.is_valid():
            cleaned_form = view_form.cleaned_data
            ctx["articulos"] = Article.objects.filter(
                codigo=int(cleaned_form['buscar']))  # Código de barras
    else:
        view_form = FormBusqueda()

    return HttpResponse(template.render(ctx, request))


@login_required
def articulo(request, codigo_articulo):
    """Modify  an existing article."""
    template = loader.get_template('agregar_modificar.html')
    new_article = Article.objects.filter(codigo=codigo_articulo).first()
    if new_article is None:
        return redirect('not_found')

    form_details = {
        'codigo': new_article.codigo,
        'descripcion': new_article.descripcion,
        'en_dolar': new_article.en_dolar,
        'costo': new_article.costo,
        'porcentaje_ganancia': new_article.porcentaje_ganancia,
        'porcentaje_descuento': new_article.porcentaje_descuento,
        'seccion': new_article.seccion,
        'marca': new_article.marca,
        'modelo': new_article.modelo,
        'stock': new_article.stock,
        'alarma_stock': new_article.alarma_stock
    }
    view_form = FormNuevoArticulo(form_details)
    ctx = {
        "articulos": Article.objects.filter(id__lte=50),
        "form": view_form,
        "titulo": "Modificar Artículo"
    }

    if request.method == "POST":
        view_form = FormNuevoArticulo(request.POST)
        if view_form.is_valid():
            cleaned_form = view_form.cleaned_data

            if all(cleaned_form['costo'], cleaned_form['costo_sin_iva']):
                ctx['mensaje'] = ("PROBLEMA: Los campos costo final y costo "
                    "neto + IVA estan completados. Debes llenar solo uno de "
                    "estos dos campos.")

            elif cleaned_form['costo'] is not None or cleaned_form['costo_sin_iva'] is not None:

                new_article.codigo = cleaned_form['codigo']
                if cleaned_form['descripcion'] != "":
                    new_article.descripcion = cleaned_form['descripcion']
                new_article.en_dolar = cleaned_form['en_dolar']
                new_article.costo_sin_iva = cleaned_form['costo_sin_iva']
                new_article.costo = Article.get_context(cleaned_form)['costo']
                new_article.porcentaje_ganancia = cleaned_form['porcentaje_ganancia']
                new_article.precio_sin_iva = Article.get_context(cleaned_form)['precio_sin_iva']
                new_article.precio = Article.get_context(cleaned_form)['precio']
                new_article.porcentaje_descuento = Article.get_context(cleaned_form)['porcentaje_descuento']
                new_article.precio_descontado = Article.get_context(cleaned_form)['precio_descontado']
                if cleaned_form['seccion'] != "":
                    new_article.seccion = cleaned_form['seccion']
                new_article.marca = cleaned_form['marca']
                new_article.modelo = cleaned_form['modelo']
                new_article.stock = cleaned_form['stock']
                new_article.alarma_stock = cleaned_form['alarma_stock']
                new_article.save()  # Guardamos los cambios en la base de datos

                return redirect('control_inventario')

            else:
                ctx['mensaje'] = "PROBLEMA: Debes rellenar uno de los dos costos."
                view_form = FormNuevoArticulo(form_details)

    else:
        view_form = FormNuevoArticulo(form_details)

    return HttpResponse(template.render(ctx, request))


# Funciones para administrar las ventas
@login_required
def venta(request):
    template = loader.get_template('venta.html')
    view_form = FormVenta({'cantidad': 1, 'dni_cliente': dni_cliente()})
    article_status = ArtState.objects.get(nombre="Active") # Creamos un ArtState instance para definir una transacción Activa
    lista = []
    ctx = {
        "articulo_a_vender": venta_activa()[0],
        "form": view_form,
        "titulo": "Venta",
        "total": venta_activa()[1].total,
        "cliente": "",
        "descuento": venta_activa()[1].descuento,
        "total_con_descuento": venta_activa()[1].total_con_descuento
    }
    if venta_activa()[1].cliente is not None:
        ctx['cliente'] = venta_activa()[1].cliente.nombre

    if request.method == "POST":
        view_form = FormVenta(request.POST)
        if view_form.is_valid():
            cleaned_form = view_form.cleaned_data  # Sacamos los datos del formulario en un diccionario y lo metemos a una variable

            ##
            # Venta
            ##

            try: # Si ya hay un objeto activo, solo agregarle elementos de tipo detalle_Venta a su id
                nueva_venta = Venta.objects.get(id_state=article_status)

            except ObjectDoesNotExist as DoesNotExist: # Si no hay ninguno activo, crearlo.
                nueva_venta = Venta.objects.create(fecha=date.today(),
                                                   total=0,
                                                   id_state=article_status,
                                                   descuento=0,
                                                   cliente=buscar_cliente(cleaned_form['dni_cliente'])) # Iniciar un objeto de tipo Venta (id(auto), fecha, id_state=1(active), total=0)
            else:
                if cleaned_form['dni_cliente'] is not None:
                    nueva_venta.cliente = buscar_cliente(cleaned_form['dni_cliente'])

                elif cleaned_form['cliente'] is not None:
                    try:
                        nueva_venta.cliente = buscar_cliente(cleaned_form['cliente'])
                    except:
                        nueva_venta.cliente = None
                        ctx['cliente'] = "Hay más de un cliente con el mismo nombre, probar con DNI."

                nueva_venta.save()

            ##
            # Articulo
            ##

            try: # Si el producto existe en la base de datos
                new_article = Article.objects.get(codigo=cleaned_form['codigo']) # Llamamos al objeto desde la db que tenga el mismo codigo que en
                                                                            # el formulario y lo metemos como QuerySet en una variable.
                ctx["article_detail"] = new_article
                ##
                # Detalle de venta
                ##
                costo_peso_argentino = new_article.costo * PrecioDolar.cotizacion_venta() if new_article.en_dolar else new_article.costo
                precio_peso_argentino = new_article.precio * PrecioDolar.cotizacion_venta() if new_article.en_dolar else new_article.precio
                if new_article.stock >= cleaned_form['cantidad']:
                    DetalleVenta.objects.create(costo_unitario=costo_peso_argentino, # Iniciar un objeto de tipo detalle_venta
                                                precio_unitario=precio_peso_argentino,
                                                porcentaje_descuento=new_article.porcentaje_descuento,
                                                precio_por_cantidad=precio_peso_argentino * cleaned_form['cantidad'],
                                                descuento=precio_peso_argentino * new_article.porcentaje_descuento / 100,
                                                cantidad=cleaned_form['cantidad'],
                                                id_venta=Venta.objects.get(id_state=article_status),
                                                id_producto=Article.objects.get(codigo=cleaned_form['codigo']))
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
                if i.descuento is not None:
                    nueva_venta.descuento += (i.descuento * i.cantidad)
            nueva_venta.total_con_descuento = nueva_venta.total - nueva_venta.descuento

            nueva_venta.save()
            ctx['total'] = nueva_venta.total
            ctx['descuento'] = nueva_venta.descuento
            ctx['total_con_descuento'] = nueva_venta.total_con_descuento
            ctx['articulo_a_vender'] = lista
            view_form = FormVenta({'cantidad': 1, 'dni_cliente': dni_cliente()})
            ctx['form'] = view_form
            if nueva_venta.cliente is not None:
                ctx['cliente'] = nueva_venta.cliente.nombre

            return HttpResponse(template.render(ctx, request))
    else:
        # Es es formulario que se muestra antes de enviar la info. La cantidad por defecto de articulos a vender es 1.
        view_form = FormVenta({'cantidad': 1, 'dni_cliente': dni_cliente()})

    return HttpResponse(template.render(ctx, request))

@login_required
def historial_ventas(request):
    template = loader.get_template('historial_ventas.html')
    view_form = FormFiltroFecha()
    if Venta.get_inactive().exists():
        ctx = {
            "transaccion": Venta.get_inactive(),
            "form": view_form,
            "titulo": "Historial de ventas"
        }
        # Filtro fecha
        if request.method == "POST":
            view_form = FormFiltroFecha(request.POST)
            if view_form.is_valid():
                cleaned_form = view_form.cleaned_data
                ctx["transaccion"] = Venta.objects.filter(fecha__range=[cleaned_form['fecha_inicial'], cleaned_form['fecha_final']]).order_by('-fecha', '-id')
        else:
            view_form = FormFiltroFecha()
        # !filtro fecha

        return HttpResponse(template.render(ctx, request))

    else:
        return redirect('venta_exitosa')

@login_required
def recibo(request, id_venta):
    try:
        return FileResponse(emitir_recibo(id_venta), as_attachment=False, filename=f'recibo_{Venta.objects.get(id=id_venta).fecha}.pdf')
    except ObjectDoesNotExist as DoesNotExist:
        return redirect('not_found')


@login_required
def venta_exitosa(request):
    template = loader.get_template('mensaje.html')
    ctx = {'mensaje': 'Su transacción fue un éxito.',
           'titulo': 'Venta exitosa',
           'hay_recibo': False}

    article_status = ArtState.objects.get(nombre="Active")
    try:
        nueva_venta = Venta.objects.get(id_state=article_status)

        producto_leido = DetalleVenta.objects.filter(id_venta=nueva_venta)  # Se crea un QuerySet para sacar datos de cada producto comprado

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



#Funciones para administrar los clientes
@login_required
def cliente(request):
    template = loader.get_template('agregar_modificar.html')
    view_form = FormCliente()
    lista = []
    ctx = {
        "articulo_a_vender": lista,
        "form": view_form,
        "mensaje": "",
        "titulo": "Añadir cliente"
    }

    if request.method == "POST":
        view_form = FormCliente(request.POST)
        if view_form.is_valid():
            cleaned_form = view_form.cleaned_data  # Sacamos los datos del formulario en un diccionario y lo metemos a una variable

            try: # Si el cliente existe en la base de datos
                new_client = Cliente.objects.get(dni=cleaned_form['dni'])
                ctx['mensaje'] = "El cliente ya existe"

            except ObjectDoesNotExist as DoesNotExist: # Si el cliente no existe en la base de datos, crearlo
                new_client = Cliente.objects.create(nombre=cleaned_form['nombre'],
                                                    condicion_iva=cleaned_form['condicion_iva'],
                                                    dni=cleaned_form['dni'],
                                                    cuit=cleaned_form['cuit'],
                                                    direccion=cleaned_form['direccion'],
                                                    telefono=cleaned_form['telefono'],
                                                    email=cleaned_form['email'])

                return redirect('control_clientes')

            view_form = FormCliente()

    return HttpResponse(template.render(ctx, request))

@login_required
def control_clientes(request):
    template = loader.get_template('control_personas.html')
    view_form = FormBusqueda()
    ctx = {
        "titulo": "Lista de clientes",
        "articulos": Cliente.objects.filter(id__lte=50).order_by('nombre'),
        "agregar_persona": "+ Agregar Cliente",
        "link_agregar": "/cliente",
        "link_modificar": "/modificar_cliente/",
        "form": view_form
    }

    if request.method == "POST":
        view_form = FormBusqueda(request.POST)
        if view_form.is_valid():
            cleaned_form = view_form.cleaned_data
            resultado = Cliente.objects.filter(dni=int(cleaned_form['buscar'])) # Código
            ctx["articulos"] = resultado
    else:
        view_form = FormBusqueda()

    return HttpResponse(template.render(ctx, request))

@login_required
def modificar_cliente(request, id_param):
    template = loader.get_template('agregar_modificar.html')
    try:
        new_cliente = Cliente.objects.get(id=id_param)
    except ObjectDoesNotExist as DoesNotExist:
        return redirect('not_found')
    else:
        form_details = {
            'nombre': new_cliente.nombre,
            'condicion_iva': new_cliente.condicion_iva,
            'dni': new_cliente.dni,
            'cuit': new_cliente.cuit,
            'direccion': new_cliente.direccion,
            'telefono': new_cliente.telefono,
            'email': new_cliente.email
        }
        view_form = FormCliente(form_details)
        ctx = {
            "articulos": Cliente.objects.filter(id__lte=50),
            "form": view_form,
            "mensaje": "",
            "titulo": "Modificar cliente"
        }

        if request.method == "POST":
            view_form = FormCliente(request.POST)
            if view_form.is_valid():
                cleaned_form = view_form.cleaned_data  # Sacamos los datos del formulario en un diccionario y lo metemos a una variable

                new_cliente.nombre = cleaned_form["nombre"]
                new_cliente.condicion_iva = cleaned_form["condicion_iva"]
                new_cliente.dni = cleaned_form["dni"]
                new_cliente.cuit = cleaned_form["cuit"]
                new_cliente.direccion = cleaned_form["direccion"]
                new_cliente.telefono = cleaned_form["telefono"]
                new_cliente.email = cleaned_form["email"]

                new_cliente.save()

                return redirect('control_clientes')

        return HttpResponse(template.render(ctx, request))


#Funciones para administrar los proveedores
@login_required
def proveedor(request):
    template = loader.get_template('agregar_modificar.html')
    view_form = FormProveedor()
    lista = []
    ctx = {
        "articulo_a_vender": lista,
        "form": view_form,
        "mensaje": "",
        "titulo": "Añadir proveedor"
    }

    if request.method == "POST":
        view_form = FormProveedor(request.POST)
        if view_form.is_valid():
            cleaned_form = view_form.cleaned_data  # Sacamos los datos del formulario en un diccionario y lo metemos a una variable

            try: # Si el Proveedor existe en la base de datos
                new_proveedor = Proveedor.objects.get(nombre=cleaned_form['nombre'])
                ctx['mensaje'] = "El proveedor ya existe"

            except ObjectDoesNotExist as DoesNotExist: # Si el Proveedor no existe en la base de datos, crearlo
                new_proveedor = Proveedor.objects.create(nombre=cleaned_form['nombre'],
                                                         condicion_iva=cleaned_form['condicion_iva'],
                                                         cuit=cleaned_form['cuit'],
                                                         direccion=cleaned_form['direccion'],
                                                         telefono=cleaned_form['telefono'],
                                                         email=cleaned_form['email'])

                ctx['mensaje'] = 'El proveedor fue agregado correctamente.'

            view_form = FormProveedor()

    return HttpResponse(template.render(ctx, request))

@login_required
def modificar_proveedor(request, id_param):
    template = loader.get_template('agregar_modificar.html')
    try:
        new_proveedor = Proveedor.objects.get(id=id_param)
    except ObjectDoesNotExist as DoesNotExist:
        return redirect('not_found')
    else:
        form_details = {
            'nombre': new_proveedor.nombre,
            'condicion_iva': new_proveedor.condicion_iva,
            'cuit': new_proveedor.cuit,
            'direccion': new_proveedor.direccion,
            'telefono': new_proveedor.telefono,
            'email': new_proveedor.email
        }
        view_form = FormProveedor(form_details)
        ctx = {
            "articulos": Proveedor.objects.filter(id__lte=50),
            "form": view_form,
            "mensaje": "",
            "titulo": "Modificar proveedor"
        }

        if request.method == "POST":
            view_form = FormProveedor(request.POST)
            if view_form.is_valid():
                # Sacamos los datos del formulario en un diccionario y lo metemos a una variable
                cleaned_form = view_form.cleaned_data

                new_proveedor.nombre = cleaned_form["nombre"]
                new_proveedor.condicion_iva = cleaned_form["condicion_iva"]
                new_proveedor.cuit = cleaned_form["cuit"]
                new_proveedor.direccion = cleaned_form["direccion"]
                new_proveedor.telefono = cleaned_form["telefono"]
                new_proveedor.email = cleaned_form["email"]

                new_proveedor.save()

                return redirect('control_clientes')

        return HttpResponse(template.render(ctx, request))

@login_required
def control_proveedores(request):
    template = loader.get_template('control_personas.html')
    ctx = {
        "titulo": "Proveedores",
        "articulos": Proveedor.objects.filter(id__lte=50).order_by('nombre'),
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