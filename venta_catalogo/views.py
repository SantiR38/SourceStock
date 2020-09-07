from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.template import Template, Context, loader
from erp.models import Article
from venta_catalogo.forms import FormFiltrarArticulos
from erp.functions import inventario, stock_total

# Create your views here.
def venta_por_catalogo(request):
    template = loader.get_template('venta_catalogo/venta.html')
    miFormulario = FormFiltrarArticulos()
    ctx = {
        "datos_generales": stock_total(),
        "articulos": inventario(Article).order_by('descripcion'),
        "form": miFormulario
    }

    if request.method == "POST":
        miFormulario = FormFiltrarArticulos(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data
            resultado = Article.objects.filter(codigo=int(infForm['codigo'])) # Código
            ctx["articulos"] = resultado
    else:
        miFormulario = FormFiltrarArticulos()

    return HttpResponse(template.render(ctx, request))