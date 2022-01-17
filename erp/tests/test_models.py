from datetime import date
from django.test import TestCase

from erp.models import Client, Sale


class ClienteTestCase(TestCase):
    def setUp(self):
        Client.objects.create(name="Santi Rodriguez",
            tax_condition=Client.TAX_SINGLE_PAYER,
            dni=39249727,
            cuit="20-39249727-8",
            direction="Mariquita S. de Thompson 1580",
            phone_number="3585163434",
            email="santirodriguez38@gmail.com")


class VentaTestCase(TestCase):
    def test_create_sale(self):
        sale = Sale.crear_venta_vacia(Sale.STATUS_WAITING)
        self.assertEqual(sale.datetime_created, date.today())
        self.assertEqual(sale.total, 0)
        self.assertEqual(sale.discount, 0)
        self.assertEqual(sale.extra_discount, 0)
        self.assertEqual(sale.total_discounted, None)
