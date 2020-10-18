from django.urls import path
from . import views
from .views import HistorialDeVenta, HistorialDeCompra


urlpatterns = [
    path('', views.venta, name='venta'),
    path('agregar_articulo', views.agregar_articulo, name='agregar_articulo'),
    path('entrada', views.entrada, name='entrada'),
    path('transaccion_exitosa', views.transaccion_exitosa, name='transaccion_exitosa'),
    path('venta_exitosa', views.venta_exitosa, name='venta_exitosa'),
    path('cancelar', views.cancelar, name='cancelar'),
    path('cliente', views.cliente, name='cliente'),
    path('modificar_cliente/<int:id_param>', views.modificar_cliente, name='modificar_cliente'),
    path('modificar_proveedor/<int:id_param>', views.modificar_proveedor, name='modificar_proveedor'),
    path('proveedor', views.proveedor, name='proveedor'),
    path('control_inventario', views.control_inventario, name='control_inventario'),
    path('control_clientes', views.control_clientes, name='control_clientes'),
    path('control_proveedores', views.control_proveedores, name='control_proveedores'),
    path('articulo/<int:codigo_articulo>', views.articulo, name='articulo'),
    path('cancelar_unidad/<int:codigo_articulo>', views.cancelar_unidad, name='cancelar_unidad'),
    path('script_actualizacion', views.script_actualizacion, name='script_actualizacion'),
    path('recibo/<int:id_venta>', views.recibo, name='recibo'),
    path('detalle_entrada/<int:id_entrada>', views.detalle_entrada, name='detalle_entrada'),
    path('historial_ventas', views.historial_ventas, name='historial_ventas'),
    path('historial_de_venta/<int:year>/<int:month>/', HistorialDeVenta.as_view(month_format='%m')),
    path('historial_de_compra/<int:year>/<int:month>/',
         HistorialDeCompra.as_view(month_format='%m'),
         name="historial_de_compra"),
    path('not_found', views.not_found, name='not_found'),
    path('historial_compras', views.historial_compras, name='historial_compras')
]

