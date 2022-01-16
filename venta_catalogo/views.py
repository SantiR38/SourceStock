from datetime import date

from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.template import Template, Context, loader
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from erp.models import Article, Venta, DetalleVenta, Client
from venta_catalogo.forms import FormFiltrarArticulos, FormBuscarCliente
from venta_catalogo.forms import FormDescuentoAdicional
from erp.functions import venta_activa, emitir_recibo, venta_activa_dict
from .functions.search_engines import search_articles, search_clients
from api.models import PrecioDolar

@login_required
def venta_por_catalogo(request):
    PrecioDolar.actualizar_registro()
    template = loader.get_template('venta_catalogo/venta.html')
    miFormulario = FormFiltrarArticulos()
    ctx = {
        "articulo_a_vender": venta_activa()[0],
        "totales": venta_activa()[1],
        "titulo": "Venta por catálogo",
        "articulos": Article.objects.filter(id__lte=50).order_by('description'),
        "form": miFormulario
    }

    if request.method == "POST":
        miFormulario = FormFiltrarArticulos(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data
            resultado = search_articles(infForm)
            ctx["articulos"] = resultado
    else:
        miFormulario = FormFiltrarArticulos()

    return HttpResponse(template.render(ctx, request))

@login_required
def aniadir_al_carrito(request, code_param):

    nueva_venta = Venta.objects.get(status=Venta.STATUS_WAITING)

    new_article = Article.objects.get(code=code_param)

    ##
    # Detalle de venta
    ##
    costo_peso_argentino = new_article.cost * PrecioDolar.cotizacion_venta() if new_article.is_in_dolar else new_article.cost
    precio_peso_argentino = new_article.price * PrecioDolar.cotizacion_venta() if new_article.is_in_dolar else new_article.price
    DetalleVenta.objects.create(costo_unitario=costo_peso_argentino, # Iniciar un objeto de tipo detalle_venta
                                precio_unitario=precio_peso_argentino,
                                discount_percentage=new_article.discount_percentage,
                                precio_por_cantidad= precio_peso_argentino,
                                descuento=precio_peso_argentino * new_article.discount_percentage / 100,
                                quantity=1,
                                id_venta=nueva_venta,
                                product_id=new_article)

    return redirect('venta_por_catalogo')

@login_required
def confirmar_venta(request):
    template = loader.get_template('venta_catalogo/confirmar_operacion.html')
    miFormulario = FormBuscarCliente()

    ctx = {
        "articulo_a_vender": venta_activa_dict(),
        "esta_venta": venta_activa()[1],
        "titulo": "Confirmar venta",
        "persona": Client.objects.all(),
        "person_title": "Cliente",
        "form": miFormulario
    }

    nueva_venta = Venta.objects.get(status=Venta.STATUS_WAITING)

    if request.method == "POST":
        miFormulario = FormBuscarCliente(request.POST)
        if miFormulario.is_valid():
            ctx["persona"] = search_clients(miFormulario.cleaned_data) # Código simplificado
    else:
        miFormulario = FormBuscarCliente()

    return HttpResponse(template.render(ctx, request))

@login_required
def elegir_cliente(request, code_param):

    nueva_venta = Venta.objects.get(status=Venta.STATUS_WAITING)

    nueva_venta.cliente = Client.objects.get(id=code_param)
    nueva_venta.save()

    return redirect('confirmar_venta')

@login_required
def descuento_adicional(request):
    template = loader.get_template('venta_catalogo/descuento_adicional.html')
    miFormulario = FormDescuentoAdicional()
    nueva_venta = venta_activa()[1]

    ctx = {
        "form": miFormulario,
        "articulo_a_vender": venta_activa()[0],
        "esta_venta": venta_activa()[1],
        "titulo": "Añadir descuento adicional",
        "person_title": "Cliente",

    }
    if request.method == "POST":
        miFormulario = FormDescuentoAdicional(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data
            nueva_venta.descuento_adicional = nueva_venta.total * infForm['descuento'] / 100
            nueva_venta.total_con_descuento -= nueva_venta.descuento_adicional
            nueva_venta.save()
            return redirect('venta_exitosa')

    return HttpResponse(template.render(ctx, request))

@login_required
def presupuesto(request, id_venta):
    try:
        return FileResponse(emitir_recibo(id_venta), as_attachment=True, filename=f'presupuesto_{date.today()}.pdf')
    except ObjectDoesNotExist as DoesNotExist:
        return redirect('not_found')