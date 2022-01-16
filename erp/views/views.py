from datetime import date

from django.shortcuts import redirect
from django.http import HttpResponse, FileResponse, HttpResponseRedirect
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from api.models import PrecioDolar
from erp.forms import (FormVenta, FormNuevoArticulo, FormEntrada, FormCliente,
    FormBusqueda, FormFiltroFecha, FormProveedor)
from erp.models import (Article, Purchase, DetalleEntrada, Venta,
    DetalleVenta, Client, Provider)
from erp.functions import (profit_percentage, venta_activa, compra_activa,
    buscar_cliente, comprar_articulo, buscar_proveedor, dni_cliente,
    emitir_recibo, nombre_proveedor, emitir_detalle_entrada)


@login_required
def entrada(request):
    template = loader.get_template('entrada.html')
    view_form = FormEntrada(
        {'quantity': 1, 'provider': nombre_proveedor()})
    ctx = {
        "articulo_a_comprar": compra_activa()[0],
        "form": view_form,
        "titulo": "Compra",
        "total": compra_activa()[1].total,
        "porcentaje_inexistente": "",
        "provider": ""
    }
    if compra_activa()[1].provider is not None:
        ctx['provider'] = compra_activa()[1].provider.name

    if request.method == "POST":
        view_form = FormEntrada(request.POST)
        if view_form.is_valid():
            # Sacamos los datos del formulario en un diccionario y lo metemos a una variable
            cleaned_form = view_form.cleaned_data
            # Si ya hay un objeto activo, solo agregarle
            # elementos de tipo detalle_entrada a su id
            new_sale = Purchase.objects.filter(status=Purchase.STATUS_WAITING).first()
            if new_sale is None:
                new_sale = Purchase.objects.create(datetime_created=cleaned_form['datetime_created'],
                    total=0, status=Purchase.STATUS_WAITING)
            new_sale.provider = buscar_proveedor(cleaned_form['provider'])
            new_sale.save()

            new_article = Article.objects.filter(
                code=cleaned_form['code']).first()
            if new_article is None:
                ctx['inexistente'] = ('Artículo inexistente, debe agregarlo en'
                    'la sección "Control de inventario/Agregar artículo". El '
                    'resto de la compra seguirá guardada.')
            elif new_article.profit_percentage is None:
                ctx["porcentaje_inexistente"] = ("Este producto no tiene "
                    "porcentaje de ganancia. Agrégalo en la sección "
                    "'Agregar o modificar' antes de continuar.")
            else:
                if cleaned_form.get('inexistente') is None:
                    DetalleEntrada.objects.create(cost_no_taxes=comprar_articulo(cleaned_form)['cost_no_taxes'],
                        unit_cost=comprar_articulo(cleaned_form)['cost'],
                        cost_by_quantity=comprar_articulo(cleaned_form)['cost'] * comprar_articulo(cleaned_form)['quantity'],
                        quantity=comprar_articulo(cleaned_form)['quantity'],
                        purchase_id=new_sale,
                        is_in_dolar=comprar_articulo(cleaned_form)['is_in_dolar'],
                        product_id=new_article)
                    ctx['inexistente'] = ''

            queryset = DetalleEntrada.objects.filter(purchase_id=new_sale)
            new_sale.total = 0
            for i in queryset:
                if i.is_in_dolar:
                    new_sale.total += (i.unit_cost * i.quantity * PrecioDolar.cotizacion_venta())
                else:
                    new_sale.total += (i.unit_cost * i.quantity)  # Se suman los precios unitarios al price total de la compra
            new_sale.save()
            ctx['total'] = new_sale.total
            ctx['articulo_a_comprar'] = queryset

            view_form = FormEntrada({'quantity': 1, 'provider': nombre_proveedor()})

            if compra_activa()[1].provider is not None:
                ctx['provider'] = compra_activa()[1].provider.name
            return HttpResponse(template.render(ctx, request))
    else:
        # Es es formulario que se muestra antes de enviar la info. La quantity por defecto de articulos a comprar es 1.
        view_form = FormEntrada({'quantity': 1, 'provider': nombre_proveedor()})

    return HttpResponse(template.render(ctx, request))


@login_required
def transaccion_exitosa(request):
    template = loader.get_template('message.html')
    ctx = {'message': 'Su transacción fue un éxito.',
           'titulo': 'Transacción exitosa',
           'redireccion': 'Volviendo a la página de ventas...'}

    nueva_venta = Purchase.objects.filter(status=Purchase.STATUS_WAITING).first()
    if nueva_venta is None:
        return redirect('not_found')

    producto_leido = DetalleEntrada.objects.filter(
        purchase_id=nueva_venta).select_related('product_id')

    try:
        for j in producto_leido:  # Esto es simplemente para que cancele la compra completa y no se actualicen el stock y price solo de algunos productos
            j.product_id.profit_percentage * 1  # Es una multiplicacion que solo sirve para poner en evidencia el error (porque un numero no se puede multiplicar por 'None')
        for i in producto_leido:  # Se actualiza el cost y el stock de cada objeto Article
            i.product_id.is_in_dolar = i.is_in_dolar
            i.product_id.cost_no_taxes = i.cost_no_taxes
            i.product_id.cost = i.unit_cost
            i.product_id.price_no_taxes = profit_percentage(i.cost_no_taxes, i.product_id.profit_percentage)
            i.product_id.price = profit_percentage(i.unit_cost, i.product_id.profit_percentage)
            i.product_id.discounted_price = profit_percentage(i.product_id.price, -i.product_id.discount_percentage)
            i.product_id.stock += i.quantity
            i.product_id.save()

        nueva_venta.status = Purchase.STATUS_FINISHED
        nueva_venta.save()  # Hace que esa entrada pase a estar inactiva
    except TypeError:
        ctx['message'] = ('Error. Uno o varios artículos no poseen porcentaje '
            'de ganancia. Agregalos en "Agregar o Modificar" Luego registra '
            'nuevamente la compra.')
        nueva_venta = Purchase.objects.get(status=Purchase.STATUS_WAITING)
        nueva_venta.delete()  # Deletes sale_details in cascade

    return HttpResponse(template.render(ctx, request))

@login_required
def historial_compras(request):
    template = loader.get_template('historial_ventas.html')
    view_form = FormFiltroFecha()

    if not Purchase.get_inactive().exists():
        return redirect('venta_exitosa')
    
    ctx = {
        "transaccion": Purchase.get_inactive(),
        "form": view_form,
        "titulo": "Historial de compras"
    }
    # Filtro fecha
    if request.method == "POST":
        view_form = FormFiltroFecha(request.POST)
        if view_form.is_valid():
            cleaned_form = view_form.cleaned_data
            ctx["transaccion"] = Purchase.objects.filter(
                fecha__range=[cleaned_form['fecha_inicial'], cleaned_form['fecha_final']]
            ).order_by('-datetime_created', '-id')
    else:
        view_form = FormFiltroFecha()

    return HttpResponse(template.render(ctx, request))
        

@login_required
def detalle_entrada(request, purchase_id):
    purchase = Purchase.objects.filter(id=purchase_id).first()
    if purchase is None:
        return redirect('not_found')

    return FileResponse(emitir_detalle_entrada(purchase_id),
        as_attachment=False, filename=f'detalle_entrada_{purchase.datetime_created}.pdf')


@login_required
def cancelar(request):
    """
    Cancel transacciont view.
    ---
    Delete all the instances `Purchase` and `Venta` with STATUS_WAITING`.
    Useful only for sales and purchases.
    """
    template = loader.get_template('message.html')
    Purchase.objects.filter(status=Purchase.STATUS_WAITING).delete()
    Venta.objects.filter(status=Purchase.STATUS_WAITING).delete()

    ctx = {'message': 'Se ha cancelado la transacción.',
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
            ctx['message'] = Article.create_new(view_form.cleaned_data)
            view_form = FormNuevoArticulo()
    else:
        view_form = FormNuevoArticulo()
    return HttpResponse(template.render(ctx, request))


@login_required
def control_inventario(request):
    template = loader.get_template('control_inventario.html')
    view_form = FormBusqueda()
    ctx = {
        "articulos": Article.objects.filter(id__lte=50).order_by('description'),
        "form": view_form,
        "titulo": "Control de inventario"
    }

    if request.method == "POST":
        view_form = FormBusqueda(request.POST)
        if view_form.is_valid():
            cleaned_form = view_form.cleaned_data
            ctx["articulos"] = Article.objects.filter(
                code=int(cleaned_form['buscar']))  # Código de barras
    else:
        view_form = FormBusqueda()

    return HttpResponse(template.render(ctx, request))


@login_required
def articulo(request, code_articulo):
    """Modify  an existing article."""
    template = loader.get_template('agregar_modificar.html')
    new_article = Article.objects.filter(code=code_articulo).first()
    if new_article is None:
        return redirect('not_found')

    form_details = {
        'code': new_article.code,
        'description': new_article.description,
        'is_in_dolar': new_article.is_in_dolar,
        'cost': new_article.cost,
        'profit_percentage': new_article.profit_percentage,
        'discount_percentage': new_article.discount_percentage,
        'section': new_article.section,
        'brand': new_article.brand,
        'model': new_article.model,
        'stock': new_article.stock,
        'min_stock_allowed': new_article.min_stock_allowed
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

            if all(cleaned_form['cost'], cleaned_form['cost_no_taxes']):
                ctx['message'] = ("PROBLEMA: Los campos cost final y cost "
                    "neto + IVA estan completados. Debes llenar solo uno de "
                    "estos dos campos.")

            elif cleaned_form['cost'] is not None or cleaned_form['cost_no_taxes'] is not None:

                new_article.code = cleaned_form['code']
                if cleaned_form['description'] != "":
                    new_article.description = cleaned_form['description']
                new_article.is_in_dolar = cleaned_form['is_in_dolar']
                new_article.cost_no_taxes = cleaned_form['cost_no_taxes']
                new_article.cost = Article.get_context(cleaned_form)['cost']
                new_article.profit_percentage = cleaned_form['profit_percentage']
                new_article.price_no_taxes = Article.get_context(cleaned_form)['price_no_taxes']
                new_article.price = Article.get_context(cleaned_form)['price']
                new_article.discount_percentage = Article.get_context(cleaned_form)['discount_percentage']
                new_article.discounted_price = Article.get_context(cleaned_form)['discounted_price']
                if cleaned_form['section'] != "":
                    new_article.section = cleaned_form['section']
                new_article.brand = cleaned_form['brand']
                new_article.model = cleaned_form['model']
                new_article.stock = cleaned_form['stock']
                new_article.min_stock_allowed = cleaned_form['min_stock_allowed']
                new_article.save()  # Guardamos los cambios en la base de datos

                return redirect('control_inventario')

            else:
                ctx['message'] = "PROBLEMA: Debes rellenar uno de los dos costos."
                view_form = FormNuevoArticulo(form_details)

    else:
        view_form = FormNuevoArticulo(form_details)

    return HttpResponse(template.render(ctx, request))


# Funciones para administrar las ventas
@login_required
def venta(request):
    template = loader.get_template('venta.html')
    view_form = FormVenta({'quantity': 1, 'dni_cliente': dni_cliente()})
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
        ctx['cliente'] = venta_activa()[1].cliente.name

    if request.method == "POST":
        view_form = FormVenta(request.POST)
        if view_form.is_valid():
            cleaned_form = view_form.cleaned_data  # Sacamos los datos del formulario en un diccionario y lo metemos a una variable

            ##
            # Venta
            ##

            try:  # Si ya hay un objeto activo, solo agregarle elementos de tipo detalle_Venta a su id
                nueva_venta = Venta.objects.get(status=Venta.STATUS_WAITING)

            except Venta.DoesNotExist:
                nueva_venta = Venta.objects.create(
                    total=0,
                    status=Venta.STATUS_WAITING,
                    descuento=0,
                    cliente=buscar_cliente(cleaned_form['dni_cliente']))
            else:
                if cleaned_form['dni_cliente'] is not None:
                    nueva_venta.cliente = buscar_cliente(cleaned_form['dni_cliente'])

                elif cleaned_form['cliente'] is not None:
                    try:
                        nueva_venta.cliente = buscar_cliente(cleaned_form['cliente'])
                    except:
                        nueva_venta.cliente = None
                        ctx['cliente'] = "Hay más de un cliente con el mismo name, probar con DNI."

                nueva_venta.save()

            ##
            # Articulo
            ##

            try: # Si el producto existe en la base de datos
                new_article = Article.objects.get(code=cleaned_form['code']) # Llamamos al objeto desde la db que tenga el mismo code que en
                                                                            # el formulario y lo metemos como QuerySet en una variable.
                ctx["article_detail"] = new_article
                ##
                # Detalle de venta
                ##
                costo_peso_argentino = new_article.cost * PrecioDolar.cotizacion_venta() if new_article.is_in_dolar else new_article.cost
                precio_peso_argentino = new_article.price * PrecioDolar.cotizacion_venta() if new_article.is_in_dolar else new_article.price
                if new_article.stock >= cleaned_form['quantity']:
                    DetalleVenta.objects.create(unit_cost=costo_peso_argentino, # Iniciar un objeto de tipo detalle_venta
                                                precio_unitario=precio_peso_argentino,
                                                discount_percentage=new_article.discount_percentage,
                                                precio_por_cantidad=precio_peso_argentino * cleaned_form['quantity'],
                                                descuento=precio_peso_argentino * new_article.discount_percentage / 100,
                                                quantity=cleaned_form['quantity'],
                                                id_venta=Venta.objects.get(status=Venta.STATUS_WAITING),
                                                product_id=Article.objects.get(code=cleaned_form['code']))
                else:
                    ctx['inexistente'] = 'No hay suficiente stock del producto.'

            except ObjectDoesNotExist as DoesNotExist: # Si el producto no existe en la base de datos
                ctx['inexistente'] = 'Artículo inexistente, debe agregarlo en la sección "Control de inventario/Agregar artículo". El resto de la venta seguirá guardada.'

            # Se suman los precios unitarios al price total de la venta
            lista = DetalleVenta.objects.filter(id_venta=nueva_venta)
            nueva_venta.total = 0
            nueva_venta.descuento = 0
            for i in lista:
                nueva_venta.total += (i.precio_unitario * i.quantity)
                if i.descuento is not None:
                    nueva_venta.descuento += (i.descuento * i.quantity)
            nueva_venta.total_con_descuento = nueva_venta.total - nueva_venta.descuento

            nueva_venta.save()
            ctx['total'] = nueva_venta.total
            ctx['descuento'] = nueva_venta.descuento
            ctx['total_con_descuento'] = nueva_venta.total_con_descuento
            ctx['articulo_a_vender'] = lista
            view_form = FormVenta({'quantity': 1, 'dni_cliente': dni_cliente()})
            ctx['form'] = view_form
            if nueva_venta.cliente is not None:
                ctx['cliente'] = nueva_venta.cliente.name

            return HttpResponse(template.render(ctx, request))
    else:
        # Es es formulario que se muestra antes de enviar la info. La cantidad por defecto de articulos a vender es 1.
        view_form = FormVenta({'quantity': 1, 'dni_cliente': dni_cliente()})

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
                ctx["transaccion"] = Venta.objects.filter(fecha__range=[cleaned_form['fecha_inicial'], cleaned_form['fecha_final']]).order_by('-datetime_created', '-id')
        else:
            view_form = FormFiltroFecha()
        # !filtro fecha

        return HttpResponse(template.render(ctx, request))

    else:
        return redirect('venta_exitosa')

@login_required
def recibo(request, id_venta):
    try:
        return FileResponse(emitir_recibo(id_venta), as_attachment=False, filename=f'recibo_{Venta.objects.get(id=id_venta).datetime_created}.pdf')
    except ObjectDoesNotExist as DoesNotExist:
        return redirect('not_found')


@login_required
def venta_exitosa(request):
    template = loader.get_template('message.html')
    ctx = {'message': 'Su transacción fue un éxito.',
           'titulo': 'Venta exitosa',
           'hay_recibo': False}

    try:
        nueva_venta = Venta.objects.get(status=Venta.STATUS_WAITING)

        producto_leido = DetalleVenta.objects.filter(id_venta=nueva_venta)  # Se crea un QuerySet para sacar datos de cada producto comprado

        if producto_leido.exists():
            for i in producto_leido: # Se actualiza  el stock de cada objeto Article
                i.product_id.stock -= i.quantity
                i.product_id.save()

            nueva_venta.status = Venta.STATUS_FINISHED
            nueva_venta.save()
            ctx['hay_recibo'] = True
        else:
            return redirect('not_found')
        ctx['id_venta'] = nueva_venta.id
    except Venta.DoesNotExist:
        return redirect('not_found')


    return HttpResponse(template.render(ctx, request))

@login_required
def cancelar_unidad(request, code_articulo):
    try:
        articulo_staging = DetalleVenta.objects.get(id=code_articulo)
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
        "message": "",
        "titulo": "Añadir cliente"
    }

    if request.method == "POST":
        view_form = FormCliente(request.POST)
        if view_form.is_valid():
            cleaned_form = view_form.cleaned_data  # Sacamos los datos del formulario en un diccionario y lo metemos a una variable

            try: # Si el cliente existe en la base de datos
                new_client = Client.objects.get(dni=cleaned_form['dni'])
                ctx['message'] = "El cliente ya existe"

            except ObjectDoesNotExist as DoesNotExist: # Si el cliente no existe en la base de datos, crearlo
                new_client = Client.objects.create(name=cleaned_form['name'],
                                                    tax_condition=cleaned_form['tax_condition'],
                                                    dni=cleaned_form['dni'],
                                                    cuit=cleaned_form['cuit'],
                                                    direction=cleaned_form['direction'],
                                                    phone_number=cleaned_form['phone_number'],
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
        "articulos": Client.objects.filter(id__lte=50).order_by('name'),
        "agregar_persona": "+ Agregar Cliente",
        "link_agregar": "/cliente",
        "link_modificar": "/modificar_cliente/",
        "form": view_form
    }

    if request.method == "POST":
        view_form = FormBusqueda(request.POST)
        if view_form.is_valid():
            cleaned_form = view_form.cleaned_data
            resultado = Client.objects.filter(dni=int(cleaned_form['buscar'])) # Código
            ctx["articulos"] = resultado
    else:
        view_form = FormBusqueda()

    return HttpResponse(template.render(ctx, request))

@login_required
def modificar_cliente(request, id_param):
    template = loader.get_template('agregar_modificar.html')
    try:
        new_cliente = Client.objects.get(id=id_param)
    except ObjectDoesNotExist as DoesNotExist:
        return redirect('not_found')
    else:
        form_details = {
            'name': new_cliente.name,
            'tax_condition': new_cliente.tax_condition,
            'dni': new_cliente.dni,
            'cuit': new_cliente.cuit,
            'direction': new_cliente.direction,
            'phone_number': new_cliente.phone_number,
            'email': new_cliente.email
        }
        view_form = FormCliente(form_details)
        ctx = {
            "articulos": Client.objects.filter(id__lte=50),
            "form": view_form,
            "message": "",
            "titulo": "Modificar cliente"
        }

        if request.method == "POST":
            view_form = FormCliente(request.POST)
            if view_form.is_valid():
                cleaned_form = view_form.cleaned_data  # Sacamos los datos del formulario en un diccionario y lo metemos a una variable

                new_cliente.name = cleaned_form["name"]
                new_cliente.tax_condition = cleaned_form["tax_condition"]
                new_cliente.dni = cleaned_form["dni"]
                new_cliente.cuit = cleaned_form["cuit"]
                new_cliente.direction = cleaned_form["direction"]
                new_cliente.phone_number = cleaned_form["phone_number"]
                new_cliente.email = cleaned_form["email"]

                new_cliente.save()

                return redirect('control_clientes')

        return HttpResponse(template.render(ctx, request))


#Funciones para administrar los proveedores
@login_required
def provider(request):
    template = loader.get_template('agregar_modificar.html')
    view_form = FormProveedor()
    lista = []
    ctx = {
        "articulo_a_vender": lista,
        "form": view_form,
        "message": "",
        "titulo": "Añadir provider"
    }

    if request.method == "POST":
        view_form = FormProveedor(request.POST)
        if view_form.is_valid():
            cleaned_form = view_form.cleaned_data  # Sacamos los datos del formulario en un diccionario y lo metemos a una variable

            try: # Si el Provider existe en la base de datos
                new_proveedor = Provider.objects.get(name=cleaned_form['name'])
                ctx['message'] = "El provider ya existe"

            except ObjectDoesNotExist as DoesNotExist: # Si el Provider no existe en la base de datos, crearlo
                new_proveedor = Provider.objects.create(name=cleaned_form['name'],
                                                         tax_condition=cleaned_form['tax_condition'],
                                                         cuit=cleaned_form['cuit'],
                                                         direction=cleaned_form['direction'],
                                                         phone_number=cleaned_form['phone_number'],
                                                         email=cleaned_form['email'])

                ctx['message'] = 'El provider fue agregado correctamente.'

            view_form = FormProveedor()

    return HttpResponse(template.render(ctx, request))

@login_required
def modificar_proveedor(request, id_param):
    template = loader.get_template('agregar_modificar.html')
    try:
        new_proveedor = Provider.objects.get(id=id_param)
    except ObjectDoesNotExist as DoesNotExist:
        return redirect('not_found')
    else:
        form_details = {
            'name': new_proveedor.name,
            'tax_condition': new_proveedor.tax_condition,
            'cuit': new_proveedor.cuit,
            'direction': new_proveedor.direction,
            'phone_number': new_proveedor.phone_number,
            'email': new_proveedor.email
        }
        view_form = FormProveedor(form_details)
        ctx = {
            "articulos": Provider.objects.filter(id__lte=50),
            "form": view_form,
            "message": "",
            "titulo": "Modificar provider"
        }

        if request.method == "POST":
            view_form = FormProveedor(request.POST)
            if view_form.is_valid():
                # Sacamos los datos del formulario en un diccionario y lo metemos a una variable
                cleaned_form = view_form.cleaned_data

                new_proveedor.name = cleaned_form["name"]
                new_proveedor.tax_condition = cleaned_form["tax_condition"]
                new_proveedor.cuit = cleaned_form["cuit"]
                new_proveedor.direction = cleaned_form["direction"]
                new_proveedor.phone_number = cleaned_form["phone_number"]
                new_proveedor.email = cleaned_form["email"]

                new_proveedor.save()

                return redirect('control_clientes')

        return HttpResponse(template.render(ctx, request))

@login_required
def control_proveedores(request):
    template = loader.get_template('control_personas.html')
    ctx = {
        "titulo": "Proveedores",
        "articulos": Provider.objects.filter(id__lte=50).order_by('name'),
        "agregar_persona": "+ Agregar Provider",
        "link_agregar": "/provider",
        "link_modificar": "/modificar_proveedor/"
    }

    return HttpResponse(template.render(ctx, request))

@login_required
def not_found(request):
    template = loader.get_template('error_404.html')
    ctx = {"titulo": "Error 404. Su solicitud no fue encontrada."}
    return HttpResponse(template.render(ctx, request))