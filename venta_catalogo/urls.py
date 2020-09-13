from django.urls import path
from . import views

urlpatterns = [
    path('', views.venta_por_catalogo, name='venta_por_catalogo'),
    path('aniadir_al_carrito/<int:codigo_param>', views.aniadir_al_carrito, name='aniadir_al_carrito'),
    path('elegir_cliente/<int:codigo_param>', views.elegir_cliente, name='elegir_cliente'),
    path('confirmar_venta', views.confirmar_venta, name='confirmar_venta'),

]
