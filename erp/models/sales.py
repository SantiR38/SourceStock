# noqa
from django.db import models

from erp.models.articles import Article
from erp.models.base import BaseOperationModel, SSBaseModel
from erp.models.persons import Client


class Sale(BaseOperationModel):
    total = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    extra_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_discounted = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)

    @classmethod
    def crear_venta_vacia(cls, status):
        sale = cls.objects.create(
            total=0,
            status=status,
            discount=0,
            extra_discount=0)
        return sale

    @classmethod
    def get_active(cls):
        return cls.objects.filter(status=cls.STATUS_WAITING).first()

    @classmethod
    def get_inactive(cls):
        """
        Shows the last 50 sales made.
        """
        return cls.objects.filter(status=cls.STATUS_FINISHED) \
            .order_by('-datetime_created', '-id')[:50]


class SaleDetail(SSBaseModel):
    sale_id = models.ForeignKey('Sale', on_delete=models.CASCADE)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_by_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_id = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()

    @classmethod
    def take_product_back(cls, param):
        products = cls.objects.filter(sale_id=param)
        for i in products:
            if i.product_id.stock >= i.quantity:
                i.product_id.stock += i.quantity
                i.product_id.save()
