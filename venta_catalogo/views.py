from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.template import Template, Context, loader
from erp.models import Article
from erp.forms import FormBusqueda
from erp.functions import inventario, stock_total

# Create your views here.
def venta_por_catalogo(request):
    template = loader.get_template('venta_catalogo/venta.html')
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