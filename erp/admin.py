from django.contrib import admin
from erp.models import Article, Purchase, DetalleEntrada, Sale, SaleDetail, Loss, LossDetail, Client


class ArticleAdmin(admin.ModelAdmin):
    list_display = ("code", "description", "cost", "profit_percentage", "price", "section", "stock")
    search_fields = ("code", "description")
    list_filter = ("section",)


class DetalleEntradaAdmin(admin.ModelAdmin):
    list_display = ("purchase_id", "product_id", "unit_cost", "quantity")


admin.site.register(Article, ArticleAdmin)
admin.site.register(Purchase)
admin.site.register(DetalleEntrada, DetalleEntradaAdmin)
admin.site.register(Sale)
admin.site.register(SaleDetail)
admin.site.register(Loss)
admin.site.register(LossDetail)
admin.site.register(Client)