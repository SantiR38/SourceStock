from django.contrib import admin
from erp.models import Article, Entrada, DetalleEntrada, Venta, DetalleVenta, Loss, LossDetail, Cliente


class ArticleAdmin(admin.ModelAdmin):
    list_display = ("code", "description", "cost", "profit_percentage", "price", "section", "stock")
    search_fields = ("code", "description")
    list_filter = ("section",)


class DetalleEntradaAdmin(admin.ModelAdmin):
    list_display = ("id_entrada", "id_producto", "costo_unitario", "cantidad")


admin.site.register(Article, ArticleAdmin)
admin.site.register(Entrada)
admin.site.register(DetalleEntrada, DetalleEntradaAdmin)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(Loss)
admin.site.register(LossDetail)
admin.site.register(Cliente)