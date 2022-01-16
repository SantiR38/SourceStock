from django.contrib import admin
from erp.models import Article, Entrada, DetalleEntrada, Venta, DetalleVenta, Perdida, DetallePerdida, Cliente

# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    list_display = ("code", "descripcion", "costo", "porcentaje_ganancia", "precio", "seccion", "stock")
    search_fields = ("code", "descripcion")
    list_filter = ("seccion",) # Comma is important, because this is a tupple. Otherwise gives us an Exception.

class DetalleEntradaAdmin(admin.ModelAdmin):
    list_display = ("id_entrada", "id_producto", "costo_unitario", "cantidad")

admin.site.register(Article, ArticleAdmin)
admin.site.register(Entrada)
admin.site.register(DetalleEntrada, DetalleEntradaAdmin)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(Perdida)
admin.site.register(DetallePerdida)
admin.site.register(Cliente)