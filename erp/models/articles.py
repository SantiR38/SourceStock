# noqa
from decimal import Decimal
from django.db import models

from erp.models import SSBaseModel


class Article(SSBaseModel):
    description = models.CharField(max_length=100, null=True)
    cost_no_taxes = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    profit_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_no_taxes = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    section = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    stock = models.IntegerField(verbose_name="Cantidad")
    min_stock_allowed = models.IntegerField(verbose_name="Stock minimo permitido", null=True)
    is_in_dolar = models.BooleanField(default=False, null=True,
        help_text="Determines if the product cotization is in dolar.")

    @classmethod
    def get_porcentaje_ganancia(self, cost, porcentaje):
        # Calcula el porcentaje de ganancia mediante los dos parámetros solicitados.
        final_price = cost + (cost * porcentaje / 100)
        return final_price

    @classmethod
    def get_context(cls, infForm):
        cost_no_taxes = infForm['cost_no_taxes']
        cost = infForm['cost']
        discount_percentage = infForm['discount_percentage']
        discounted_price = None
        if cost_no_taxes is not None:
            cost = cls.get_porcentaje_ganancia(cost_no_taxes, 21)
        elif cost is not None:
            cost_no_taxes = cost / Decimal(1.21)

        price = cls.get_porcentaje_ganancia(cost, infForm['profit_percentage'])

        if discount_percentage is not None:
            discounted_price = cls.get_porcentaje_ganancia(price, -discount_percentage)

        context = {
            "code": infForm['code'],
            "description": infForm['description'],
            "cost_no_taxes": cost_no_taxes,
            "cost": cost,
            "price_no_taxes": cls.get_porcentaje_ganancia(cost_no_taxes, infForm['profit_percentage']),
            "price": price,
            "profit_percentage": infForm['profit_percentage'],
            "discount_percentage": discount_percentage,
            "discounted_price": discounted_price,
            "section": infForm['section'],
            "brand": infForm['brand'],
            "model": infForm['model'],
            "stock": infForm['stock'],
            "min_stock_allowed": infForm['min_stock_allowed'],
            "is_in_dolar": infForm['is_in_dolar']
        }

        return context

    @classmethod
    def create_new(cls, infForm):
        article = cls.objects.filter(code=infForm['code'])
        if article.exists():
            message = "El código ya está siendo utilizado por otro producto."
        else:
            if infForm['cost'] is not None and infForm['cost_no_taxes'] is not None:
                message = "PROBLEMA: Los campos cost final y cost neto + IVA estan completados. Debes llenar solo uno de estos dos campos."
            elif infForm['cost'] is not None or infForm['cost_no_taxes'] is not None:
                cls.objects.create(code=cls.get_context(infForm)['code'],
                    description=cls.get_context(infForm)['description'],
                    cost_no_taxes=cls.get_context(infForm)['cost_no_taxes'],
                    cost=cls.get_context(infForm)['cost'],
                    is_in_dolar=cls.get_context(infForm)['is_in_dolar'],
                    price_no_taxes=cls.get_context(infForm)['price_no_taxes'],
                    price=cls.get_context(infForm)['price'],
                    profit_percentage=cls.get_context(infForm)['profit_percentage'],
                    discount_percentage=cls.get_context(infForm)['discount_percentage'],
                    discounted_price=cls.get_context(infForm)['discounted_price'],
                    section=cls.get_context(infForm)['section'],
                    brand=cls.get_context(infForm)['brand'],
                    model=cls.get_context(infForm)['model'],
                    stock=cls.get_context(infForm)['stock'],
                    min_stock_allowed=cls.get_context(infForm)['min_stock_allowed'])
                message = "Artículo agregado exitosamente"
            else:
                message = "PROBLEMA: Debes rellenar uno de los dos costos."
        return message

    def __str__(self):
        return self.description
