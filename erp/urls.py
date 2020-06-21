from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('agregar_modificar', views.agregar_modificar, name='agregar_modificar'),
    path('compra_simple', views.compra_simple, name='compra_simple'),
    path('entrada', views.entrada, name='entrada'),
    path('transaccion_exitosa', views.transaccion_exitosa, name='transaccion_exitosa'),
]