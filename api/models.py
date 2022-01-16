from decimal import Decimal

from django.db import models

from erp.models import SSBaseModel
from .services import get_dolar_value


DOLAR_VALUES = get_dolar_value()
DOLAR_COMPRA = Decimal(DOLAR_VALUES[0].replace(',','.'))
DOLAR_VENTA = Decimal(DOLAR_VALUES[1].replace(',','.'))


class PrecioDolar(SSBaseModel):
    oficial_compra = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=DOLAR_COMPRA)
    oficial_venta = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=DOLAR_VENTA)

    @classmethod
    def actualizar_registro(cls):
        registry = cls.objects.filter(id=1).first()
        if registry is not None:
            registry.oficial_compra = DOLAR_COMPRA
            registry.oficial_venta = DOLAR_VENTA
            registry.save()
        else:
            cls.objects.create()

    @classmethod
    def cotizacion_venta(cls):
        return cls.objects.get(id=1).oficial_venta
