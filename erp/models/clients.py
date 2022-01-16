# noqa
from django.db import models

from erp.models import SSBaseModel


class Cliente(SSBaseModel):
    nombre = models.CharField(max_length=50)
    condicion_iva = models.CharField(max_length=25, default="Consumidor Final")
    dni = models.PositiveIntegerField(null=True)
    cuit = models.CharField(max_length=15, null=True)
    direccion = models.CharField(max_length=50, null=True)
    telefono = models.CharField(max_length=30, null=True)
    email = models.EmailField(null=True)
