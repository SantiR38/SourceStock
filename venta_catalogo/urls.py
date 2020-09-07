from django.urls import path
from . import views

urlpatterns = [
    path('', views.venta_por_catalogo, name='venta_por_catalogo'),
    path('aniadir_al_carrito', views.aniadir_al_carrito, name='aniadir_al_carrito'),

]
