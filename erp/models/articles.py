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

    @staticmethod
    def get_porcentaje_ganancia(cost, porcentaje):
        """Calculates the profit percentage from the requested params."""
        final_price = cost + (cost * porcentaje / 100)
        return final_price

    @classmethod
    def get_context(cls, data):
        cost_no_taxes = data['cost_no_taxes']
        cost = data['cost']
        discount_percentage = data['discount_percentage']
        discounted_price = None
        if cost_no_taxes is not None:
            cost = cls.get_porcentaje_ganancia(cost_no_taxes, 21)
        elif cost is not None:
            cost_no_taxes = cost / Decimal(1.21)

        price = cls.get_porcentaje_ganancia(cost, data['profit_percentage'])

        if discount_percentage is not None:
            discounted_price = cls.get_porcentaje_ganancia(price, -discount_percentage)

        context = {
            "code": data['code'],
            "description": data['description'],
            "cost_no_taxes": cost_no_taxes,
            "cost": cost,
            "price_no_taxes": cls.get_porcentaje_ganancia(cost_no_taxes, data['profit_percentage']),
            "price": price,
            "profit_percentage": data['profit_percentage'],
            "discount_percentage": discount_percentage,
            "discounted_price": discounted_price,
            "section": data['section'],
            "brand": data['brand'],
            "model": data['model'],
            "stock": data['stock'],
            "min_stock_allowed": data['min_stock_allowed'],
            "is_in_dolar": data['is_in_dolar']
        }

        return context

    @classmethod
    def create_new(cls, data):
        article = cls.objects.filter(code=data['code'])

        if article.exists():
            return "El código ya está siendo utilizado por otro producto."

        if all(data['cost'], data['cost_no_taxes']):
            return ("PROBLEMA: Los campos cost final y cost neto + IVA "
                "estan completados. Debes llenar solo uno de estos dos campos.")

        if any(data['cost'], data['cost_no_taxes']):
            context = cls.get_context(data)
            cls.objects.create(**context)
            return "Artículo agregado exitosamente"

        return "PROBLEMA: Debes rellenar uno de los dos costos."

    def __str__(self):
        return self.description
