from django.shortcuts import render
from django.http import HttpResponse
from django.template import Template, Context, loader
from django.core.exceptions import ObjectDoesNotExist
from erp.forms import FormVenta, FormNuevoArticulo, FormEntrada
from erp.models import Article, ArtState, Entrada, DetalleEntrada, Venta, DetalleVenta, Perdida, DetallePerdida
from erp.functions import stock_total

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
                if infForm['descripcion'] != "":
                    new_article.descripcion = infForm['descripcion']
                new_article.costo = infForm['costo']
                new_article.precio = infForm['precio']
                if infForm['seccion'] != "":
                    new_article.seccion = infForm['seccion']
                new_article.save() # Guardamos los cambios de la linea anterior en la base de datos
                ctx['datos_generales'] = stock_total() # Actualiza el stock cuando se hace la compra, asi no va atrasado
            except ObjectDoesNotExist as DoesNotExist:
                new_article = Article.objects.create(codigo=infForm['codigo'], descripcion=infForm['descripcion'], precio=infForm['precio'], costo=infForm['costo'], seccion=infForm['seccion'], stock=0)
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
    miFormulario = FormEntrada({'cantidad': 1})
    lista = []
    ctx = {
        "articulo_a_comprar": lista,
        "datos_generales": stock_total(),
        "form": miFormulario
    }

    if request.method == "POST":
        miFormulario = FormEntrada(request.POST)
        if miFormulario.is_valid():
            infForm = miFormulario.cleaned_data # Sacamos los datos del formulario en un diccionario y lo metemos a una variable
            estado = ArtState.objects.get(nombre="Active") # Creamos un ArtState instance para que no tire error al referir la foreign key
            try: # Si el producto existe en la base de datos
                new_article = Article.objects.get(codigo=infForm['codigo']) # Llamamos al objeto desde la db que tenga el mismo codigo que en
                                                                            # el formulario y lo metemos como QuerySet en una variable.

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


                '''
                ctx['datos_generales'] = stock_total() # Actualiza el stock cuando se hace la compra, asi no va atrasado
                '''
                ctx['inexistente'] = ''
            except ObjectDoesNotExist as DoesNotExist: # Si el producto no existe en la base de datos
                ctx['inexistente'] = 'Artículo inexistente, debe agregarlo en la pestaña "Agregar artículo"'

            miFormulario = FormEntrada({'cantidad': 1 })
            
            return HttpResponse(template.render(ctx, request))
    else:
        # Es es formulario que se muestra antes de enviar la info. La cantidad por defecto de articulos a comprar es 1.
        miFormulario = FormEntrada({'cantidad': 1})

    return HttpResponse(template.render(ctx, request))