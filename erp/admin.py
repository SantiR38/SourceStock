from django.contrib import admin
from erp.models import Article

# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descripcion", "costo", "precio", "seccion", "stock")
    search_fields = ("codigo", "descripcion")
    list_filter = ("seccion",) # Comma is important, because this is a tupple. Otherwise gives us an Exception.

admin.site.register(Article, ArticleAdmin)