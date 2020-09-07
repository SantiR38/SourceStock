from erp.models import Article, ArtState, Venta, DetalleVenta, Cliente, Proveedor, Entrada, DetalleEntrada
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import FileResponse
from reportlab.pdfgen import canvas
from datetime import date
from decimal import *
import io

def inventario(param):

    # Almacena todos los objetos del modelo pasado por parámetro
    # en un query_set para mostrar en la vista "control de inventario".

    return param.objects.all()

def stock_total():

    # Se aplica al widget de cabecera donde se muestra:
    #   1. El stock total todos los productos.
    #   2. La cantidad de distintos productos que ofrece la empresa.

    cantidad_total = 0
    diferentes_productos = 0
    try:
        query_set = inventario(Article)
        for i in query_set:
            cantidad_total += query_set[diferentes_productos].stock
            diferentes_productos += 1
    except UnboundLocalError:
        cantidad_total = 0
        diferentes_productos = 0
    resultado = [cantidad_total, diferentes_productos]
    return resultado

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
    estado = ArtState.objects.get(nombre="Active") # Creamos un ArtState instance para definir una transacción Activa
    
    try: # Si ya hay un objeto activo, solo agregarle elementos de tipo detalle_Venta a su id
        nueva_venta = Venta.objects.get(id_state=estado)
    except ObjectDoesNotExist as DoesNotExist:
        nueva_venta = Venta.objects.create(fecha=date.today(),
                                            total=0,
                                            id_state=estado,
                                            descuento=0
                                            ) # Iniciar un objeto de tipo Venta (id(auto), fecha, id_state=1(active), total=0)
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

def campos_sin_iva():

    # Cuando la tabla solo tiene los costos y precios con iva incluidos, esta formula itera sobre cada producto
    # agregando el costo y el precio sin iva (se hace solo una vez a la hora de actualizar la app.)

    a = Article.objects.all()
    x = round((Decimal(1.21)), 2)
    for i in a:
        i.costo_sin_iva = i.costo / x
        i.precio_sin_iva = i.precio / x
        i.save()

def add_art_state():

    # Esta función es utilizada apenas se lanza el proyecto para registrar los tres campos de ArtState.

    ArtState.objects.create(nombre="Active")
    ArtState.objects.create(nombre="Inactive")
    ArtState.objects.create(nombre="Deleted")

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
    p.drawString(480, alto, "$")
    p.drawString(490, alto, str(venta.descuento))

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
    p.drawString(38, 740, "LA CASA DE LAS BATERÍAS")
    
    p.setFont("Helvetica", 10)
    p.drawString(38, 715, "Fecha de emisión:")
    p.drawString(130, 715, str(entrada.fecha))

    p.drawString(38, 693, "Dir: Av. Amadeo Sabattini 2917, Río Cuarto (Cba.)")
    p.drawString(297.5, 693, "Tel: 358 517-0913")


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

def crear_articulo(infForm):
    # Funciona solo para modificar objetos de tipo Article.
    costo_sin_iva = infForm['costo_sin_iva']
    costo = infForm['costo']
    porcentaje_descuento = infForm['porcentaje_descuento']
    precio_descontado = None
    if costo_sin_iva != None:
        costo = porcentaje_ganancia(costo_sin_iva, 21)
    elif costo != None:
        costo_sin_iva = costo / Decimal(1.21)

    precio = porcentaje_ganancia(costo, infForm['porcentaje_ganancia'])

    if porcentaje_descuento != None:
        precio_descontado = porcentaje_ganancia(precio, -porcentaje_descuento)

    contexto = {
        "codigo": infForm['codigo'],
        "descripcion": infForm['descripcion'],
        "costo_sin_iva": costo_sin_iva,
        "costo": costo,
        "precio_sin_iva": porcentaje_ganancia(costo_sin_iva, infForm['porcentaje_ganancia']),
        "precio": precio,
        "porcentaje_ganancia": infForm['porcentaje_ganancia'],
        "porcentaje_descuento": porcentaje_descuento,
        "precio_descontado": precio_descontado,
        "seccion": infForm['seccion'],
        "marca": infForm['marca'],
        "stock": infForm['stock']
    }

    return contexto

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
        "cantidad": infForm['cantidad']
    }

    return contexto