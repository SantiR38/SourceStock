from django.shortcuts import render
from django.http import HttpResponse
from django.template import Template, Context, loader
from django.core.exceptions import ObjectDoesNotExist
from erp.forms import FormVenta, FormCompra
from erp.models import Article

# Esta es una funcion comun, no es una view.
def stock_total():
    cantidad_total = 0
    diferentes_productos = 0
    try:
        query_set = Article.objects.all()
        for i in query_set:
            cantidad_total += query_set[diferentes_productos].stock
            diferentes_productos += 1
    except UnboundLocalError:
        cantidad_total = 0
        diferentes_productos = 0
    resultado = [cantidad_total, diferentes_productos]
    return resultado


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


def compra(request):
    template = loader.get_template('compra.html')
    miFormulario = FormCompra({'cantidad': 1})
    lista = []
    ctx = {
        "articulo_a_agregar": lista, 
        "datos_generales": stock_total(),
        "form": miFormulario,
    }
    # Manejo del formulario de compra
    if request.method == "POST":
        miFormulario = FormCompra(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data
            try:
                new_article = Article.objects.get(codigo=infForm['codigo'])
                if infForm['descripcion'] != "":
                    new_article.descripcion = infForm['descripcion']
                new_article.costo = infForm['costo']
                new_article.precio = infForm['precio']
                if infForm['seccion'] != "":
                    new_article.seccion = infForm['seccion']
                new_article.stock += infForm['cantidad'] # Actualizamos el stock disponible
                new_article.save() # Guardamos los cambios de la linea anterior en la base de datos
                ctx['datos_generales'] = stock_total() # Actualiza el stock cuando se hace la compra, asi no va atrasado
            except ObjectDoesNotExist as DoesNotExist:
                new_article = Article.objects.create(codigo=infForm['codigo'], descripcion=infForm['descripcion'], precio=infForm['precio'], costo=infForm['costo'], seccion=infForm['seccion'], stock=infForm['cantidad'])

            lista.append(new_article) # Colocamos el QuerySet anterior en una lista que esta en el contexto (ctx)
            miFormulario = FormCompra({'cantidad': 1})

            return HttpResponse(template.render(ctx, request))
    else:
        miFormulario = FormCompra({'cantidad': 1})

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