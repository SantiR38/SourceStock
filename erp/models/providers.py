# noqa
from django.db import models

from erp.models import SSBaseModel


class Proveedor(SSBaseModel):
    nombre = models.CharField(max_length=100)
    condicion_iva = models.CharField(max_length=25)
    cuit = models.CharField(max_length=15, null=True)
    direccion = models.CharField(max_length=50, null=True)
    telefono = models.CharField(max_length=30, null=True)
    email = models.EmailField(null=True)
