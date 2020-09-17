from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.template import Template, Context, loader
from django.contrib.auth.decorators import login_required
from erp.models import Article, ArtState, Venta, DetalleVenta, Cliente
from venta_catalogo.forms import FormFiltrarArticulos, FormBuscarCliente
from venta_catalogo.forms import FormDescuentoAdicional
from erp.functions import inventario, stock_total, venta_activa
from .functions.search_engines import search_articles, search_clients

@login_required
def venta_por_catalogo(request):
    template = loader.get_template('venta_catalogo/venta.html')
    miFormulario = FormFiltrarArticulos()
    ctx = {
        "articulo_a_vender": venta_activa()[0],
        "totales": venta_activa()[1],
        "datos_generales": stock_total(),
        "articulos": inventario(Article).order_by('descripcion'),
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
def aniadir_al_carrito(request, codigo_param):

    estado = ArtState.objects.get(nombre="Active")
    nueva_venta = Venta.objects.get(id_state=estado)

    new_article = Article.objects.get(codigo=codigo_param)

    ##
    # Detalle de venta
    ##
    DetalleVenta.objects.create(costo_unitario=new_article.costo, # Iniciar un objeto de tipo detalle_venta
                                precio_unitario=new_article.precio,
                                porcentaje_descuento=new_article.porcentaje_descuento,
                                descuento=new_article.precio * new_article.porcentaje_descuento / 100,
                                cantidad=1,
                                id_venta=nueva_venta,
                                id_producto=new_article)

    return redirect('venta_por_catalogo')

@login_required
def confirmar_venta(request):
    template = loader.get_template('venta_catalogo/confirmar_operacion.html')
    miFormulario = FormBuscarCliente()

    ctx = {
        "articulo_a_vender": venta_activa()[0],
        "esta_venta": venta_activa()[1],
        "titulo": "Confirmar venta",
        "persona": Cliente.objects.all(),
        "titulo_persona": "Cliente",
        "form": miFormulario
    }

    estado = ArtState.objects.get(nombre="Active")
    nueva_venta = Venta.objects.get(id_state=estado)

    if request.method == "POST":
        miFormulario = FormBuscarCliente(request.POST)
        if miFormulario.is_valid():
            ctx["persona"] = search_clients(miFormulario.cleaned_data) # Coódigo simplificado
    else:
        miFormulario = FormBuscarCliente()

    return HttpResponse(template.render(ctx, request))

@login_required
def elegir_cliente(request, codigo_param):

    estado = ArtState.objects.get(nombre="Active")
    nueva_venta = Venta.objects.get(id_state=estado)

    nueva_venta.cliente = Cliente.objects.get(id=codigo_param)
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
        "titulo_persona": "Cliente",

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
            