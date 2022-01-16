# noqa
from django.db import models

from erp.models import SSBaseModel


class Loss(SSBaseModel):
    fecha = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)


class LossDetail(SSBaseModel):
    id_perdida = models.ForeignKey('Loss', on_delete=models.CASCADE)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    id_producto = models.ForeignKey('Article', on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
