from erp.models import Article, ArtState, Venta, DetalleVenta, Cliente
from django.core.exceptions import ObjectDoesNotExist
from django.http import FileResponse
from reportlab.pdfgen import canvas
from datetime import date
from decimal import *
import io

def inventario():
    return Article.objects.all()

def stock_total():
    cantidad_total = 0
    diferentes_productos = 0
    try:
        query_set = inventario()
        for i in query_set:
            cantidad_total += query_set[diferentes_productos].stock
            diferentes_productos += 1
    except UnboundLocalError:
        cantidad_total = 0
        diferentes_productos = 0
    resultado = [cantidad_total, diferentes_productos]
    return resultado

def porcentaje_ganancia(costo, porcentaje):
    precio_final = costo + (costo * porcentaje / 100)
    return precio_final

#En la vista venta, esta función permite que se muestre la venta que haya en curso apenas se carga la página.
def venta_activa():
    lista = []
    estado = ArtState.objects.get(nombre="Active") # Creamos un ArtState instance para definir una transacción Activa
    try: # Si ya hay un objeto activo, solo agregarle elementos de tipo detalle_Venta a su id
        nueva_venta = Venta.objects.get(id_state=estado)
    except ObjectDoesNotExist as DoesNotExist:
        nueva_venta = Venta.objects.create(fecha=date.today(),
                                            total=0,
                                            id_state=estado) # Iniciar un objeto de tipo Venta (id(auto), fecha, id_state=1(active), total=0)
    else:
        lista = DetalleVenta.objects.filter(id_venta = nueva_venta)
        nueva_venta.total = 0
        for i in lista:
            nueva_venta.total += (i.precio_unitario * i.cantidad)
        nueva_venta.save()
    return [lista, nueva_venta]

def buscar_cliente(documento):
    try:
        cliente = Cliente.objects.get(dni=documento)
    except ObjectDoesNotExist as DoesNotExist:
        cliente = None
    return cliente

def dni_cliente():
    if venta_activa()[1].cliente != None:
        a = venta_activa()[1].cliente.dni
    else:
        a = None
    return a

# Cuando la tabla solo tiene los costos y precios con iva incluidos, esta formula itera sobre cada producto
# agregando el costo y el precio sin iva (se hace solo una vez a la hora de actualizar la app.)
def campos_sin_iva():
    a = Article.objects.all()
    x = round((Decimal(1.21)), 2)
    for i in a:
        i.costo_sin_iva = i.costo / x
        i.precio_sin_iva = i.precio / x
        i.save()

def precio_final(costo_s_iva, porc_ganancia):
    costo_final = porcentaje_ganancia(costo_s_iva, 21)
    precio_final = porc_ganancia(costo_final, porc_ganancia)
    return precio_final

def emitir_recibo(id_venta):
    venta = Venta.objects.get(id=id_venta)
    detalle_venta = DetalleVenta.objects.filter(id_venta=venta)

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.setFont("Helvetica", 26)
    p.drawString(327, 790, "Recibo") #(Ancho, Alto, "Texto")
    p.setFont("Helvetica", 10)
    p.drawString(328, 770, "Documento no válido como factura")
    p.drawString(328, 740, "Fecha de emisión:")
    p.drawString(420, 740, str(venta.fecha))
    p.drawString(328, 710, "Responsable Inscripto")
    p.drawString(462, 710, "CUIT: 20-35212998-5")

    p.drawString(38, 693, "Dir: Av. Amadeo Sabattini 2917, Río Cuarto (Cba.)")
    p.drawString(297.5, 693, "Tel: 358 517-0913")
    # p.drawString(420, 693, "Inicio Actividad: 01/01/2020") Esto se pondrá recien cuando sea factura
    p.setFont("Helvetica-Bold", 12)
    ##p.drawString(80, 790, "LA CASA DE LAS BATERÍAS")
    p.drawInlineImage("erp/static/dist/img/logo_recibo.jpg", 95, 725, width=127.8,height=89.4) 
    p.drawString(80, 710, "LA CASA DE LAS BATERÍAS")

    p.setFont("Helvetica-Bold", 10)
    p.drawString(38, 673, "Cliente: ")
    p.drawString(38, 653, "Dirección: ")
    p.drawString(297.5, 673, "Cond. IVA: ")
    p.drawString(297.5, 653, "CUIT: ")

    p.setFont("Helvetica", 10)
    if venta.cliente != None:
        p.drawString(95, 673, venta.cliente.nombre + " " + venta.cliente.apellido)
        p.drawString(95, 653, venta.cliente.direccion)
        p.drawString(355, 673, venta.cliente.condicion_iva)
        p.drawString(355, 653, venta.cliente.cuit)
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
        p.drawString(50, alto, str(i.cantidad))
        p.drawString(150, alto, i.id_producto.descripcion)
        p.drawString(380, alto, "$")
        p.drawString(390, alto, str(i.precio_unitario))
        p.drawString(480, alto, "$")
        p.drawString(490, alto, str(i.cantidad*i.precio_unitario))
        alto -= 30


    # Filas total

    alto -= 50
    p.setFont("Helvetica-Bold", 11)
    p.drawString(390, alto, "Total")
    p.drawString(480, alto, "$")
    p.drawString(490, alto, str(venta.total))


    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return buffer
    