# noqa
from django.db import models

from erp.models import SSBaseModel


class Proveedor(SSBaseModel):
    name = models.CharField(max_length=100)
    tax_condition = models.CharField(max_length=25)
    cuit = models.CharField(max_length=15, null=True)
    direction = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(max_length=30, null=True)
    email = models.EmailField(null=True)
