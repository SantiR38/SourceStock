# noqa
from django.db import models

from erp.models import SSBaseModel


class Entrada(SSBaseModel):
    fecha = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    proveedor = models.ForeignKey('Proveedor', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.fecha} ({self.id})'

    @classmethod
    def get_inactive(cls):
        """
        Shows the last 50 purchases.
        """
        queryset = cls.objects.filter(status=cls.STATUS_FINISHED)
        return queryset.order_by('-fecha', '-id')[:50]


class DetalleEntrada(SSBaseModel):
    id_entrada = models.ForeignKey('Entrada', on_delete=models.CASCADE)
    is_in_dolar = models.BooleanField(default=False, null=True)
    cost_no_taxes = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    costo_por_cantidad = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_id = models.ForeignKey('Article', on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()

    @classmethod
    def give_product_back(cls, param):
        products = cls.objects.filter(id_entrada=param)
        for i in products:
            if i.product_id.stock >= i.quantity:
                i.product_id.stock -= i.quantity
                i.product_id.save()
