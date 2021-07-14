from decimal import Decimal

from django.db import models

from .services import get_dolar_value
# Create your models here.
REQ_STATUS = 'pending'
try:
    DOLAR_VALUES = get_dolar_value()
except TypeError:
    DOLAR_COMPRA = None
    DOLAR_VENTA = None
    REQ_STATUS = 'error'
else:
    DOLAR_COMPRA = Decimal(DOLAR_VALUES[0].replace(',','.'))
    DOLAR_VENTA = Decimal(DOLAR_VALUES[1].replace(',','.'))
    REQ_STATUS = 'ok'


class PrecioDolar(models.Model):
    oficial_compra = models.DecimalField(max_digits=10, decimal_places=2,
        null=True, default=DOLAR_COMPRA)
    oficial_venta = models.DecimalField(max_digits=10, decimal_places=2,
        null=True, default=DOLAR_VENTA)

    @classmethod
    def actualizar_registro(cls):
        if REQ_STATUS == 'ok':
            registry = cls.objects.filter(id=1)
            if registry.exists():
                obj = cls.objects.get(id=1)
                obj.oficial_compra = DOLAR_COMPRA
                obj.oficial_venta = DOLAR_VENTA
                obj.save()
            else:
                cls.objects.create(oficial_venta=DOLAR_VENTA,
                    oficial_compra=DOLAR_COMPRA)
    
    @classmethod
    def cotizacion_venta(cls):
        try:
            ret = cls.objects.get(id=1).oficial_venta
        except cls.DoesNotExist:
            ret = ''
        return ret