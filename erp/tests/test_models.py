from datetime import date
from django.test import TestCase
from erp.models import Cliente, Venta, ArtState

# Create your tests here.

class ClienteTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")
        pass

    def setUp(self):
        Cliente.objects.create(nombre="Santi Rodriguez",
                               condicion_iva="Monotributista",
                               dni=39249727,
                               cuit="20-39249727-8",
                               direccion="Mariquita S. de Thompson 1580",
                               telefono="3585163434",
                               email="santirodriguez38@gmail.com"
                               )
        print("ClienteTestCase.setUp(): Completado")
        pass

    def test_false_is_false(self):
        print("Method: test_false_is_false.")
        self.assertFalse(False)

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.")
        self.assertEqual(1 + 1, 2)

class VentaTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: class VENTA.")
        pass

    def setUp(self):
        ArtState.objects.create(nombre="Active")
        print("VentaTestCase.setUp(): Completado")
        pass

    def test_crear_venta(self):
        venta = Venta.crear_venta_vacia(ArtState.objects.get(nombre="Active"))
        self.assertEqual(venta.fecha, date.today())
        self.assertEqual(venta.total, 0)
        self.assertEqual(venta.descuento, 0)
        self.assertEqual(venta.descuento_adicional, 0)
        self.assertEqual(venta.total_con_descuento, None)

