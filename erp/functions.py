from erp.models import Article, ArtState, Venta, DetalleVenta, Cliente
from django.core.exceptions import ObjectDoesNotExist
from datetime import date

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
