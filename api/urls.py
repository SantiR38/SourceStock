from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import api
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'client', api.ClientViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('/dolar', views.dolar, name='dolar')
]