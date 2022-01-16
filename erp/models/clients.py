# noqa
from django.db import models

from erp.models import SSBaseModel


class Client(SSBaseModel):
    name = models.CharField(max_length=50)
    tax_condition = models.CharField(max_length=25, default="Consumidor Final")
    dni = models.PositiveIntegerField(null=True,
        help_text="Personal identification number")
    cuit = models.CharField(max_length=15, null=True,
        help_text="Personal tax identification number")
    direction = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(max_length=30, null=True)
    email = models.EmailField(null=True)
