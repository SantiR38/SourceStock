# noqa
from datetime import date
from django.db import models

from erp.models import SSBaseModel


class Venta(SSBaseModel):
    fecha = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    descuento_adicional = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_con_descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True)

    @classmethod
    def crear_venta_vacia(cls, status):
        venta = cls.objects.create(
            fecha=date.today(),
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
            .order_by('-fecha', '-id')[:50]


class DetalleVenta(SSBaseModel):
    id_venta = models.ForeignKey('Venta', on_delete=models.CASCADE)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # Si bien tanto este dato como el del precio estan en el objeto Article,
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # es mejor guardar el producto al precio que se vendió para mejor contabilidad
    precio_por_cantidad = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    porcentaje_descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    id_producto = models.ForeignKey('Article', on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()

    @classmethod
    def take_product_back(cls, param):
        products = cls.objects.filter(id_venta=param)
        for i in products:
            if i.id_producto.stock >= i.cantidad:
                i.id_producto.stock += i.cantidad
                i.id_producto.save()
