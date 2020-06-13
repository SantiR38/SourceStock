from django.contrib import admin
from erp.models import Article, Entrada, DetalleEntrada, Venta, DetalleVenta, Perdida, DetallePerdida

# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descripcion", "costo", "precio", "seccion", "stock")
    search_fields = ("codigo", "descripcion")
    list_filter = ("seccion",) # Comma is important, because this is a tupple. Otherwise gives us an Exception.

admin.site.register(Article, ArticleAdmin)
admin.site.register(Entrada)
admin.site.register(DetalleEntrada)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(Perdida)
admin.site.register(DetallePerdida)