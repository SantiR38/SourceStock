from django.test import TestCase
from erp.functions import porcentaje_ganancia

class TestFunciones(TestCase):

    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Sin datos para dar de alta.")
        pass

    def setUp(self):
        print("setUp: Sin datos para dar de alta.")
        pass

    def test_porcentaje_ganancia(self):
        print('Method: porcentaje_ganancia con dos parámetros')
        self.assertEqual(porcentaje_ganancia(100, 21), 121)
        self.assertEqual(porcentaje_ganancia(200, 21), 242)