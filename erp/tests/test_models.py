from datetime import date
from django.test import TestCase

from erp.models import Client, Venta


class ClienteTestCase(TestCase):
    def setUp(self):
        Client.objects.create(name="Santi Rodriguez",
            tax_condition="Monotributista",
            dni=39249727,
            cuit="20-39249727-8",
            direction="Mariquita S. de Thompson 1580",
            phone_number="3585163434",
            email="santirodriguez38@gmail.com")

    def test_false_is_false(self):
        self.assertFalse(False)

    def test_one_plus_one_equals_two(self):
        self.assertEqual(1 + 1, 2)


class VentaTestCase(TestCase):
    def test_create_sale(self):
        sale = Venta.crear_venta_vacia(Venta.STATUS_WAITING)
        self.assertEqual(sale.fecha, date.today())
        self.assertEqual(sale.total, 0)
        self.assertEqual(sale.descuento, 0)
        self.assertEqual(sale.descuento_adicional, 0)
        self.assertEqual(sale.total_con_descuento, None)
