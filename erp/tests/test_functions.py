from django.test import TestCase
from erp.functions import profit_percentage

class TestFunciones(TestCase):

    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Sin datos para dar de alta.")
        pass

    def setUp(self):
        print("setUp: Sin datos para dar de alta.")
        pass

    def test_porcentaje_ganancia(self):
        print('Method: profit_percentage con dos parámetros')
        self.assertEqual(profit_percentage(100, 21), 121)
        self.assertEqual(profit_percentage(200, 21), 242)