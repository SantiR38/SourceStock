# noqa
from decimal import Decimal
from django.db import models

from erp.models import SSBaseModel


class Article(SSBaseModel):
    descripcion = models.CharField(max_length=100, null=True)
    costo_sin_iva = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    porcentaje_ganancia = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    precio_sin_iva = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    porcentaje_descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    precio_descontado = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    seccion = models.CharField(max_length=100, blank=True)
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    stock = models.IntegerField(verbose_name="Cantidad")
    alarma_stock = models.IntegerField(verbose_name="Stock minimo permitido", null=True)
    en_dolar = models.BooleanField(default=False, null=True,
        help_text="Determines if the product cotization is in dolar.")

    @classmethod
    def get_porcentaje_ganancia(self, costo, porcentaje):
        # Calcula el porcentaje de ganancia mediante los dos parámetros solicitados.
        precio_final = costo + (costo * porcentaje / 100)
        return precio_final

    @classmethod
    def get_context(cls, infForm):
        costo_sin_iva = infForm['costo_sin_iva']
        costo = infForm['costo']
        porcentaje_descuento = infForm['porcentaje_descuento']
        precio_descontado = None
        if costo_sin_iva is not None:
            costo = cls.get_porcentaje_ganancia(costo_sin_iva, 21)
        elif costo is not None:
            costo_sin_iva = costo / Decimal(1.21)

        precio = cls.get_porcentaje_ganancia(costo, infForm['porcentaje_ganancia'])

        if porcentaje_descuento is not None:
            precio_descontado = cls.get_porcentaje_ganancia(precio, -porcentaje_descuento)

        context = {
            "code": infForm['code'],
            "descripcion": infForm['descripcion'],
            "costo_sin_iva": costo_sin_iva,
            "costo": costo,
            "precio_sin_iva": cls.get_porcentaje_ganancia(costo_sin_iva, infForm['porcentaje_ganancia']),
            "precio": precio,
            "porcentaje_ganancia": infForm['porcentaje_ganancia'],
            "porcentaje_descuento": porcentaje_descuento,
            "precio_descontado": precio_descontado,
            "seccion": infForm['seccion'],
            "marca": infForm['marca'],
            "modelo": infForm['modelo'],
            "stock": infForm['stock'],
            "alarma_stock": infForm['alarma_stock'],
            "en_dolar": infForm['en_dolar']
        }

        return context

    @classmethod
    def create_new(cls, infForm):
        article = cls.objects.filter(code=infForm['code'])
        if article.exists():
            mensaje = "El código ya está siendo utilizado por otro producto."
        else:
            if infForm['costo'] is not None and infForm['costo_sin_iva'] is not None:
                mensaje = "PROBLEMA: Los campos costo final y costo neto + IVA estan completados. Debes llenar solo uno de estos dos campos."
            elif infForm['costo'] is not None or infForm['costo_sin_iva'] is not None:
                cls.objects.create(code=cls.get_context(infForm)['code'],
                    descripcion=cls.get_context(infForm)['descripcion'],
                    costo_sin_iva=cls.get_context(infForm)['costo_sin_iva'],
                    costo=cls.get_context(infForm)['costo'],
                    en_dolar=cls.get_context(infForm)['en_dolar'],
                    precio_sin_iva=cls.get_context(infForm)['precio_sin_iva'],
                    precio=cls.get_context(infForm)['precio'],
                    porcentaje_ganancia=cls.get_context(infForm)['porcentaje_ganancia'],
                    porcentaje_descuento=cls.get_context(infForm)['porcentaje_descuento'],
                    precio_descontado=cls.get_context(infForm)['precio_descontado'],
                    seccion=cls.get_context(infForm)['seccion'],
                    marca=cls.get_context(infForm)['marca'],
                    modelo=cls.get_context(infForm)['modelo'],
                    stock=cls.get_context(infForm)['stock'],
                    alarma_stock=cls.get_context(infForm)['alarma_stock'])
                mensaje = "Artículo agregado exitosamente"
            else:
                mensaje = "PROBLEMA: Debes rellenar uno de los dos costos."
        return mensaje

    def __str__(self):
        return self.descripcion
