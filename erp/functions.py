from erp.models import Article

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