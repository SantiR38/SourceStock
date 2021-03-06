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
from erp.models import ArtState, Venta, DetalleVenta, Cliente, Proveedor, Entrada, DetalleEntrada, Article

# SourceStock - Api
from api.models import PrecioDolar


# ------ SERVICES ------ #

def porcentaje_ganancia(costo, porcentaje):
    # Calcula el porcentaje de ganancia mediante los dos parámetros solicitados.
    precio_final = costo + (costo * porcentaje / 100)
    return precio_final

def venta_activa():

    # En la vista venta, muestra la venta en curso apenas se carga la página.
    # Esta función devuelve dos parámetros:
    #   1. Una lista del detalle de venta para mostrar en la vista venta
    #   2. Datos de la venta general (cliente y total).
    
    lista = []
    # Creamos un ArtState instance para definir una transacción Activa
    estado = ArtState.objects.get(nombre="Active")
    
    try: # Si ya hay un objeto activo, solo agregarle elementos de tipo detalle_Venta a su id
        nueva_venta = Venta.objects.get(id_state=estado)
    except ObjectDoesNotExist as DoesNotExist:
        nueva_venta = Venta.crear_venta_vacia(estado)

    else:
        lista = DetalleVenta.objects.filter(id_venta = nueva_venta)
        nueva_venta.total = 0
        nueva_venta.descuento = 0
        for i in lista:
            nueva_venta.total += (i.precio_unitario * i.cantidad)

            if i.descuento != None:
                nueva_venta.descuento += (i.descuento * i.cantidad)
        nueva_venta.total_con_descuento = nueva_venta.total - nueva_venta.descuento
        
        nueva_venta.save()
    return [lista, nueva_venta]

def venta_activa_dict():
    venta = venta_activa()[0].values()
    for i in range(len(venta)):
        article = Article.objects.filter(id=venta[i]["id_producto_id"]).values()[0]
        venta[i]["precio_descontado"] = venta[i]["precio_unitario"] - venta[i]["descuento"]
        venta[i]["id_producto"] = article
    return venta

def compra_activa():

    # Esta función devuelve dos parámetros:
    #   1. Una lista del detalle de compra para mostrar en la vista entrada
    #   2. Datos de la compra general (proveedor y total).

    lista = []
    estado = ArtState.objects.get(nombre="Active") # Creamos un ArtState instance para definir una transacción Activa
    try: # Si ya hay un objeto activo, solo agregarle elementos de tipo detalle_Compra a su id
        nueva_compra = Entrada.objects.get(id_state=estado)
    except ObjectDoesNotExist as DoesNotExist:
        nueva_compra = Entrada.objects.create(fecha=date.today(),
                                            total=0,
                                            id_state=estado) # Iniciar un objeto de tipo Compra (id(auto), fecha, id_state=1(active), total=0)
    else:
        lista = DetalleEntrada.objects.filter(id_entrada = nueva_compra)
        nueva_compra.total = 0
        for i in lista:
            if i.en_dolar:
                nueva_compra.total += (i.costo_unitario * i.cantidad * PrecioDolar.cotizacion_venta())
            else:
                nueva_compra.total += (i.costo_unitario * i.cantidad)
        nueva_compra.save()
    return [lista, nueva_compra]

def buscar_cliente(param):

    # Se utiliza esta función para registrar un cliente dentro de una venta.

    if type(param) == int:
        try:
            cliente = Cliente.objects.get(dni=param)
        except ObjectDoesNotExist as DoesNotExist:
            cliente = None
    elif type(param) == str:
        try:
            cliente = Cliente.objects.get(nombre=param)
        except ObjectDoesNotExist as DoesNotExist:
            cliente = None
    
    return cliente

def buscar_proveedor(name):

    # Se utiliza esta función para regustrar un proveedor dentro de una entrada.

    try:
        proveedor = Proveedor.objects.get(nombre=name)
    except ObjectDoesNotExist as DoesNotExist:
        proveedor = None
    return proveedor

def dni_cliente():

    # Esta función introduce el dni del cliente en el formulario de la vista venta.

    if venta_activa()[1].cliente != None:
        a = venta_activa()[1].cliente.dni
    else:
        a = None
    return a

def nombre_proveedor():

    # Esta función introduce el nombre del proveedor en el formulario de la vista entrada.

    if compra_activa()[1].proveedor != None:
        a = compra_activa()[1].proveedor.nombre
    else:
        a = None
    return a


def precio_final(costo_s_iva, porc_ganancia):
    
    # Devuelve el precio final de un producto al cual se le registró solo el costo sin iva.

    costo_final = porcentaje_ganancia(costo_s_iva, 21)
    precio_final = porc_ganancia(costo_final, porc_ganancia)
    return precio_final

def emitir_recibo(id_venta):

    # Esta funcion dibuja en modo canva todo el pdf que servirá como recibo.
    # Utiliza la librería reportlab

    venta = Venta.objects.get(id=id_venta)
    detalle_venta = DetalleVenta.objects.filter(id_venta=venta)
    active = ArtState.objects.get(nombre="Active")
    recibo_presupuesto = "Presupuesto" if venta.id_state == active else "Recibo"
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
    p.drawString(420, 740, str(venta.fecha))
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
    if venta.cliente != None:
        p.drawString(95, 673, venta.cliente.nombre)
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
    p.drawString(390, alto, "Subtotal")
    p.drawString(480, alto, "$")
    p.drawString(490, alto, str(venta.total))

    alto -= 35
    p.drawString(390, alto, "Descuento")
    p.drawString(480, alto, "$-")
    p.drawString(490, alto, str(venta.descuento))

    alto -= 35
    p.drawString(390, alto, "Dcto. adicional")
    p.drawString(480, alto, "$-")
    p.drawString(490, alto, str(venta.descuento_adicional))

    alto -= 35
    p.setFont("Helvetica-Bold", 11)
    p.drawString(390, alto, "Total")
    p.drawString(480, alto, "$")
    p.drawString(490, alto, str(venta.total_con_descuento))


    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return buffer

def emitir_detalle_entrada(id_entrada):

    # Esta funcion dibuja en modo canva todo el pdf que servirá como recibo.
    # Utiliza la librería reportlab

    entrada = Entrada.objects.get(id=id_entrada)
    detalle_entrada = DetalleEntrada.objects.filter(id_entrada=entrada)

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
    p.drawString(130, 715, str(entrada.fecha))

    p.drawString(38, 693, f"Dir: {enterprise['address']}")
    p.drawString(297.5, 693, f"Tel: {enterprise['phone']}")


    p.setFont("Helvetica-Bold", 10)
    p.drawString(38, 673, "Proveedor: ")
    p.drawString(38, 653, "Dirección: ")
    p.drawString(297.5, 673, "Cond. IVA: ")
    p.drawString(297.5, 653, "CUIT: ")
    
    p.setFont("Helvetica", 10)
    if entrada.proveedor != None:
        p.drawString(95, 673, entrada.proveedor.nombre)
        p.drawString(95, 653, entrada.proveedor.direccion)
        p.drawString(355, 673, entrada.proveedor.condicion_iva)
        p.drawString(355, 653, entrada.proveedor.cuit)
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
        p.drawString(50, alto, str(i.cantidad))
        p.drawString(150, alto, i.id_producto.descripcion)
        p.drawString(380, alto, "$")
        p.drawString(390, alto, str(i.costo_unitario))
        p.drawString(460, alto, "$")
        p.drawString(470, alto, str(i.cantidad*i.costo_unitario))
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

    # Lista la totalidad de los proveedores para mostrar en la vista Entrada

    query = Proveedor.objects.all().order_by('nombre')
    lista = [(" ", " ")]
    if query.exists():
        for i in query:
            lista.append((i.nombre, i.nombre))
    return lista

def lista_clientes():

    # Lista la totalidad de los clientes para mostrar en la vista Venta

    query = Cliente.objects.all().order_by('nombre')
    lista = [(" ", " ")]
    if query.exists():
        for i in query:
            lista.append((i.nombre, i.nombre))
    return lista


def comprar_articulo(infForm):
    # Funciona solo para modificar objetos de tipo DetalleEntrada.
    
    costo_sin_iva = infForm['costo_sin_iva']
    costo = infForm['costo']

    if costo_sin_iva != None:
        costo = porcentaje_ganancia(costo_sin_iva, 21)
    elif costo != None:
        costo_sin_iva = costo / Decimal(1.21)

    contexto = {
        "codigo": infForm['codigo'],
        "costo_sin_iva": costo_sin_iva,
        "costo": costo,
        "cantidad": infForm['cantidad'],
        "en_dolar": infForm['en_dolar']
    }

    return contexto
    