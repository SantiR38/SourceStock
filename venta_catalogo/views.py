from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.template import Template, Context, loader
from erp.models import Article
from venta_catalogo.forms import FormFiltrarArticulos
from erp.functions import inventario, stock_total, venta_activa
from .functions.search_engines import search_articles


def venta_por_catalogo(request):
    template = loader.get_template('venta_catalogo/venta.html')
    miFormulario = FormFiltrarArticulos()
    ctx = {
        "articulo_a_vender": venta_activa()[0],
        "totales": venta_activa()[1],
        "datos_generales": stock_total(),
        "articulos": inventario(Article).order_by('descripcion'),
        "carrito": "",
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

def aniadir_al_carrito(request, codigo_param):

    new_article = Article.objects.get(codigo=codigo_param)

    
    return redirect('venta_por_catalogo')