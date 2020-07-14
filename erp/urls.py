from django.urls import path
from . import views

urlpatterns = [
    path('', views.venta, name='venta'),
    path('agregar_articulo', views.agregar_articulo, name='agregar_articulo'),
    path('entrada', views.entrada, name='entrada'),
    path('transaccion_exitosa', views.transaccion_exitosa, name='transaccion_exitosa'),
    path('venta_exitosa', views.venta_exitosa, name='venta_exitosa'),
    path('cancelar', views.cancelar, name='cancelar'),
    path('cliente', views.cliente, name='cliente'),
    path('control_inventario', views.control_inventario, name='control_inventario'),
    path('articulo/<int:codigo_articulo>', views.articulo, name='articulo'),
    path('cancelar_unidad/<int:codigo_articulo>', views.cancelar_unidad, name='cancelar_unidad'),
    path('script_actualizacion', views.script_actualizacion, name='script_actualizacion')
]