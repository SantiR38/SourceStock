"""Functions as services."""

# Python
import io
from datetime import date
from decimal import Decimal
from reportlab.pdfgen import canvas

# Django
from django.core.exceptions import ObjectDoesNotExist

# SourceStock - Main
from punto_venta.env_variables import enterprise

# Models
from erp.models import Sale, SaleDetail, Client, Provider, Purchase, DetalleEntrada, Article

# SourceStock - Api
from api.models import PrecioDolar


# ------ SERVICES ------ #

def profit_percentage(cost, porcentaje):
    # Calcula el porcentaje de ganancia mediante los dos parámetros solicitados.
    final_price = cost + (cost * porcentaje / 100)
    return final_price

def venta_activa():

    # En la vista venta, muestra la venta en curso apenas se carga la página.
    # Esta función devuelve dos parámetros:
    #   1. Una lista del detalle de venta para mostrar en la vista venta
    #   2. Datos de la venta general (client y total).

    try:  # Si ya hay un objeto activo, solo agregarle elementos de tipo detalle_Venta a su id
        nueva_venta = Sale.objects.get(status=Sale.STATUS_WAITING)
    except Sale.DoesNotExist:
        nueva_venta = Sale.crear_venta_vacia(Sale.STATUS_WAITING)
        return [[], nueva_venta]

    lista = SaleDetail.objects.filter(sale_id = nueva_venta)
    nueva_venta.total = 0
    nueva_venta.discount = 0
    for i in lista:
        nueva_venta.total += (i.unit_price * i.quantity)

        if i.discount != None:
            nueva_venta.discount += (i.discount * i.quantity)
    nueva_venta.total_discounted = nueva_venta.total - nueva_venta.discount
    
    nueva_venta.save()
    return [lista, nueva_venta]

def venta_activa_dict():
    venta = venta_activa()[0].values()
    for i in range(len(venta)):
        article = Article.objects.filter(id=venta[i]["id_producto_id"]).values()[0]
        venta[i]["discounted_price"] = venta[i]["unit_price"] - venta[i]["discount"]
        venta[i]["product_id"] = article
    return venta

def compra_activa():

    # Esta función devuelve dos parámetros:
    #   1. Una lista del detalle de compra para mostrar en la vista entrada
    #   2. Datos de la compra general (provider y total).

    lista = []
    try: # Si ya hay un objeto activo, solo agregarle elementos de tipo detalle_Compra a su id
        nueva_compra = Purchase.objects.get(status=Purchase.STATUS_WAITING)
    except Purchase.DoesNotExist:
        nueva_compra = Purchase.objects.create(
            total=0,
            status=Purchase.STATUS_WAITING)
    else:
        lista = DetalleEntrada.objects.filter(purchase_id = nueva_compra)
        nueva_compra.total = 0
        for i in lista:
            if i.is_in_dolar:
                nueva_compra.total += (i.unit_cost * i.quantity * PrecioDolar.cotizacion_venta())
            else:
                nueva_compra.total += (i.unit_cost * i.quantity)
        nueva_compra.save()
    return [lista, nueva_compra]

def buscar_cliente(param):

    # Se utiliza esta función para registrar un client dentro de una venta.

    if type(param) == int:
        try:
            client = Client.objects.get(dni=param)
        except ObjectDoesNotExist as DoesNotExist:
            client = None
    elif type(param) == str:
        try:
            client = Client.objects.get(name=param)
        except ObjectDoesNotExist as DoesNotExist:
            client = None
    
    return client

def buscar_proveedor(name):

    # Se utiliza esta función para regustrar un provider dentro de una entrada.

    try:
        provider = Provider.objects.get(name=name)
    except ObjectDoesNotExist as DoesNotExist:
        provider = None
    return provider

def dni_cliente():

    # Esta función introduce el dni del client en el formulario de la vista venta.

    if venta_activa()[1].client != None:
        a = venta_activa()[1].client.dni
    else:
        a = None
    return a

def nombre_proveedor():

    # Esta función introduce el name del provider en el formulario de la vista entrada.

    if compra_activa()[1].provider != None:
        a = compra_activa()[1].provider.name
    else:
        a = None
    return a


def final_price(costo_s_iva, porc_ganancia):
    
    # Devuelve el price final de un producto al cual se le registró solo el cost sin iva.

    costo_final = profit_percentage(costo_s_iva, 21)
    final_price = porc_ganancia(costo_final, porc_ganancia)
    return final_price

def emitir_recibo(sale_id):

    # Esta funcion dibuja en modo canva todo el pdf que servirá como recibo.
    # Utiliza la librería reportlab

    venta = Sale.objects.get(id=sale_id)
    detalle_venta = SaleDetail.objects.filter(sale_id=venta)
    recibo_presupuesto = "Presupuesto" if venta.status == Sale.STATUS_WAITING else "Recibo"
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.setFont("Helvetica", 26)
    
    p.drawString(327, 790, recibo_presupuesto) #(Ancho, Alto, "Texto")
    p.setFont("Helvetica", 10)
    p.drawString(328, 770, "Documento no válido como factura")
    p.drawString(328, 740, "Fecha de emisión:")
    p.drawString(420, 740, str(venta.datetime_created))
    p.drawString(328, 710, enterprise['iva_situation'])
    p.drawString(462, 710, f"CUIT: {enterprise['cuit']}")
    if 'cuit2' in enterprise:
        p.drawString(462, 725, f"CUIT: {enterprise['cuit2']}")

    p.drawString(38, 693, f"Dir: {enterprise['address']}")
    p.drawString(297.5, 693, f"Tel: {enterprise['phone']}")
    # p.drawString(420, 693, "Inicio Actividad: 01/01/2020") Esto se pondrá recien cuando sea factura
    p.setFont("Helvetica-Bold", 12)
    ##p.drawString(80, 790, "LA CASA DE LAS BATERÍAS")
    if 'image' in enterprise:
        p.drawInlineImage(enterprise['image'], 95, 725, width=127.8,height=89.4)
    p.drawString(80, 710, enterprise['name'])

    p.setFont("Helvetica-Bold", 10)
    p.drawString(38, 673, "Cliente: ")
    p.drawString(38, 653, "Dirección: ")
    p.drawString(297.5, 673, "Cond. IVA: ")
    p.drawString(297.5, 653, "CUIT: ")

    p.setFont("Helvetica", 10)
    if venta.client != None:
        p.drawString(95, 673, venta.client.name)
        p.drawString(95, 653, venta.client.direction)
        p.drawString(355, 673, venta.client.tax_condition)
        p.drawString(355, 653, venta.client.cuit)
    else:
        p.drawString(355, 673, "Consumidor Final")

    # Header
    p.line(30, 820, 565, 820) #Horizontal Grande
    p.line(30, 690, 565, 690) #Horizontal Grande
    p.line(30, 820, 30, 690) #Vertical Izq
    p.line(565, 820, 565, 690) #Vertical Der
    p.line(30, 705, 565, 705) #Horizontal Grande
    p.line(297.5, 785, 297.5, 705) #Vertical medio
    p.line(318, 785, 318, 820) #Vertical
    p.line(277, 785, 277, 820) #Vertical
    p.line(277, 785, 318, 785)

    p.setFont("Helvetica", 30)
    p.drawString(288, 790, "X")




    #Titulos de tabla
    alto = 600
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, alto, "Cantidad")
    p.drawString(150, alto, "Detalles")
    p.drawString(390, alto, "P. Unitario")
    p.drawString(490, alto, "P. Total")
    p.line(50, 590, 535, 590)

    # Articulos a vender
    alto = 550
    p.setFont("Helvetica", 11)

    for i in detalle_venta:
        p.drawString(50, alto, str(i.quantity))
        p.drawString(150, alto, i.product_id.description)
        p.drawString(380, alto, "$")
        p.drawString(390, alto, str(i.unit_price))
        p.drawString(480, alto, "$")
        p.drawString(490, alto, str(i.quantity*i.unit_price))
        alto -= 30


    # Filas total

    alto -= 50
    p.drawString(390, alto, "Subtotal")
    p.drawString(480, alto, "$")
    p.drawString(490, alto, str(venta.total))

    alto -= 35
    p.drawString(390, alto, "Descuento")
    p.drawString(480, alto, "$-")
    p.drawString(490, alto, str(venta.discount))

    alto -= 35
    p.drawString(390, alto, "Dcto. adicional")
    p.drawString(480, alto, "$-")
    p.drawString(490, alto, str(venta.extra_discount))

    alto -= 35
    p.setFont("Helvetica-Bold", 11)
    p.drawString(390, alto, "Total")
    p.drawString(480, alto, "$")
    p.drawString(490, alto, str(venta.total_discounted))


    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return buffer

def emitir_detalle_entrada(purchase_id):

    # Esta funcion dibuja en modo canva todo el pdf que servirá como recibo.
    # Utiliza la librería reportlab

    entrada = Purchase.objects.get(id=purchase_id)
    detalle_entrada = DetalleEntrada.objects.filter(purchase_id=entrada)

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.setFont("Helvetica", 26)
    p.drawString(38, 780, "Registro de compra") #(Ancho, Alto, "Texto")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(38, 740, enterprise['name'])
    
    p.setFont("Helvetica", 10)
    p.drawString(38, 715, "Fecha de emisión:")
    p.drawString(130, 715, str(entrada.datetime_created))

    p.drawString(38, 693, f"Dir: {enterprise['address']}")
    p.drawString(297.5, 693, f"Tel: {enterprise['phone']}")


    p.setFont("Helvetica-Bold", 10)
    p.drawString(38, 673, "Proveedor: ")
    p.drawString(38, 653, "Dirección: ")
    p.drawString(297.5, 673, "Cond. IVA: ")
    p.drawString(297.5, 653, "CUIT: ")
    
    p.setFont("Helvetica", 10)
    if entrada.provider != None:
        p.drawString(95, 673, entrada.provider.name)
        p.drawString(95, 653, entrada.provider.direction)
        p.drawString(355, 673, entrada.provider.tax_condition)
        p.drawString(355, 653, entrada.provider.cuit)
    else:
        p.drawString(355, 673, "Consumidor Final")
    
    # Header
    p.line(30, 820, 565, 820) #Horizontal Grande
    p.line(30, 690, 565, 690) #Horizontal Grande
    p.line(30, 820, 30, 690) #Vertical Izq
    p.line(565, 820, 565, 690) #Vertical Der
    p.line(30, 705, 565, 705) #Horizontal Grande


    #Titulos de tabla
    alto = 600
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, alto, "Cantidad")
    p.drawString(150, alto, "Detalles")
    p.drawString(380, alto, "Costo u.")
    p.drawString(460, alto, "Costo Total")
    p.line(50, 590, 535, 590)

    # Articulos a vender
    alto = 550
    p.setFont("Helvetica", 11)

    for i in detalle_entrada:
        p.drawString(50, alto, str(i.quantity))
        p.drawString(150, alto, i.product_id.description)
        p.drawString(380, alto, "$")
        p.drawString(390, alto, str(i.unit_cost))
        p.drawString(460, alto, "$")
        p.drawString(470, alto, str(i.quantity*i.unit_cost))
        alto -= 30

    # Filas total

    alto -= 50
    p.setFont("Helvetica-Bold", 11)
    p.drawString(390, alto, "Total")
    p.drawString(460, alto, "$")
    p.drawString(470, alto, str(entrada.total))


    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return buffer

def lista_proveedores():

    # Lista la totalidad de los proveedores para mostrar en la vista Purchase

    query = Provider.objects.all().order_by('name')
    lista = [(" ", " ")]
    if query.exists():
        for i in query:
            lista.append((i.name, i.name))
    return lista

def lista_clientes():

    # Lista la totalidad de los clientes para mostrar en la vista Sale

    query = Client.objects.all().order_by('name')
    lista = [(" ", " ")]
    if query.exists():
        for i in query:
            lista.append((i.name, i.name))
    return lista


def comprar_articulo(infForm):
    # Funciona solo para modificar objetos de tipo DetalleEntrada.
    
    cost_no_taxes = infForm['cost_no_taxes']
    cost = infForm['cost']

    if cost_no_taxes != None:
        cost = profit_percentage(cost_no_taxes, 21)
    elif cost != None:
        cost_no_taxes = cost / Decimal(1.21)

    contexto = {
        "code": infForm['code'],
        "cost_no_taxes": cost_no_taxes,
        "cost": cost,
        "quantity": infForm['quantity'],
        "is_in_dolar": infForm['is_in_dolar']
    }

    return contexto
    