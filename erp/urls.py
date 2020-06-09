from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('compra', views.compra, name='compra'),
    path('compra_simple', views.compra_simple, name='compra_simple'),
]