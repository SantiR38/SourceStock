"""punto_venta URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#from datetime import date
from django.contrib import admin
from django.urls import include, path
from api.api import UserAPI, ClientViewSet
#from django.conf.urls import handler404
#from erp.views import error_404

urlpatterns = [
        path('syslurl_des/', admin.site.urls),
        path('', include('erp.urls')),
        path('venta_catalogo/', include('venta_catalogo.urls')),
        path('accounts/', include('django.contrib.auth.urls')),
        path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
        path('api', include('api.urls')),
    ]
'''
#Opcion para que caduque un sitio de pruebas
fecha_expiracion = date(2020, 9, 15)
if date.today() < fecha_expiracion:
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', include('erp.urls')),
        path('venta_catalogo/', include('venta_catalogo.urls')),
        path('accounts/', include('django.contrib.auth.urls')),
    ]
else:
    urlpatterns = [
        path('accounts/', include('django.contrib.auth.urls')),
    ]
'''
#handler404 = error_404
