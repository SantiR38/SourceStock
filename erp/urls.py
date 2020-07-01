from django.urls import path
from . import views

urlpatterns = [
    path('', views.venta, name='venta'),
    path('salida', views.index, name='salida'),
    path('agregar_modificar', views.agregar_modificar, name='agregar_modificar'),
    path('compra_simple', views.compra_simple, name='compra_simple'),
    path('entrada', views.entrada, name='entrada'),
    path('transaccion_exitosa', views.transaccion_exitosa, name='transaccion_exitosa'),
    path('venta_exitosa', views.venta_exitosa, name='venta_exitosa'),
    path('cancelar', views.cancelar, name='cancelar'),
    path('cliente', views.cliente, name='cliente'),
]