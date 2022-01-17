# noqa
from django.db import models

from erp.models.articles import Article
from erp.models.base import BaseOperationModel, SSBaseModel
from erp.models.persons import Provider


class Purchase(BaseOperationModel):
    total = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.ForeignKey(Provider, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.datetime_created} ({self.id})'

    @classmethod
    def get_inactive(cls):
        """
        Shows the last 50 purchases.
        """
        queryset = cls.objects.filter(status=cls.STATUS_FINISHED)
        return queryset.order_by('-datetime_created', '-id')[:50]


class DetalleEntrada(SSBaseModel):
    purchase_id = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    is_in_dolar = models.BooleanField(default=False, null=True)
    cost_no_taxes = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    cost_by_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_id = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()

    @classmethod
    def give_product_back(cls, param):
        products = cls.objects.filter(purchase_id=param)
        for i in products:
            if i.product_id.stock >= i.quantity:
                i.product_id.stock -= i.quantity
                i.product_id.save()
