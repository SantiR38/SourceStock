from erp.models import Article

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