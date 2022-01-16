# noqa
from datetime import date
from django.db import models

from erp.models import SSBaseModel


class Venta(SSBaseModel):
    total = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    descuento_adicional = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_con_descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cliente = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True)

    @classmethod
    def crear_venta_vacia(cls, status):
        venta = cls.objects.create(
            total=0,
            status=status,
            descuento=0,
            descuento_adicional=0)
        return venta

    @classmethod
    def get_active(cls):
        return cls.objects.filter(status=cls.STATUS_WAITING).first()

    @classmethod
    def get_inactive(cls):
        """
        Muestra las últimas 50 ventas realizadas
        """
        return cls.objects.filter(status=cls.STATUS_FINISHED) \
            .order_by('-datetime_created', '-id')[:50]


class DetalleVenta(SSBaseModel):
    id_venta = models.ForeignKey('Venta', on_delete=models.CASCADE)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)  # Si bien tanto este dato como el del price estan en el objeto Article,
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # es mejor guardar el producto al price que se vendió para mejor contabilidad
    precio_por_cantidad = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    product_id = models.ForeignKey('Article', on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()

    @classmethod
    def take_product_back(cls, param):
        products = cls.objects.filter(id_venta=param)
        for i in products:
            if i.product_id.stock >= i.quantity:
                i.product_id.stock += i.quantity
                i.product_id.save()
