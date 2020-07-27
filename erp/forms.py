from django import forms
from datetime import date

class FormBusqueda(forms.Form):
    buscar = forms.IntegerField(label= "Código del producto")

class FormVenta(forms.Form): # Sirve para la actualización inventario en general
    codigo = forms.IntegerField(label_suffix= "*:")
    cantidad = forms.IntegerField(label_suffix= "*:")
    dni_cliente = forms.IntegerField(required=False, label="DNI Cliente")

class FormNuevoArticulo(forms.Form):
    codigo = forms.IntegerField(label_suffix= "*:")
    descripcion = forms.CharField(required=False)
    costo_sin_iva = forms.DecimalField(max_digits=10,
                                       decimal_places=2,
                                       label_suffix= "*:",
                                       label="Costo sin IVA",
                                       required=False)
    costo = forms.DecimalField(max_digits=10,
                               decimal_places=2,
                               label_suffix= "*:",
                               label="Costo con IVA",
                               required=False)
    porcentaje_ganancia = forms.DecimalField(max_digits=10, decimal_places=2, label_suffix= "*:")
    seccion = forms.CharField(required=False)
    stock = forms.IntegerField(label_suffix= "*:")

class FormEntrada(forms.Form):
    codigo = forms.IntegerField(label_suffix= "*:")
    costo_sin_iva = forms.DecimalField(max_digits=10,
                                       decimal_places=2,
                                       label="Costo sin IVA",
                                       label_suffix= "**:",
                                       required=False)
    costo = forms.DecimalField(max_digits=10,
                               decimal_places=2,
                               label="Costo con IVA",
                               label_suffix= "**:",
                               required=False)
    cantidad = forms.IntegerField(label_suffix= "*:")
    fecha = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), 
                                label_suffix= "*:",
                                initial=date.today())

class FormCliente(forms.Form):
    OPTIONS = [("Consumidor Final", "Consumidor Final"),
               ("Responsable Inscripto", "Responsable Inscripto"),
               ("Monotributista", "Monotributista"),
               ("IVA Excento", "IVA Excento"),
               ("No Alcanzado", "No Alcanzado"),
               ]

    nombre = forms.CharField(max_length=50, label_suffix= "*:")
    apellido = forms.CharField(max_length=50, label_suffix= "*:")
    condicion_iva = forms.ChoiceField(choices=OPTIONS, label= "Condición IVA", label_suffix= "*:")
    dni = forms.IntegerField(label= "DNI", label_suffix= "*:")
    cuit = forms.CharField(required=False)
    direccion = forms.CharField(max_length=50, required=False)
    telefono = forms.CharField(required=False)
    email = forms.EmailField(required=False)

class FormFiltroFecha(forms.Form):
    fecha_inicial = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), 
                                label_suffix= "*:",
                                initial=date.today())
    fecha_final = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), 
                                label_suffix= "*:",
                                initial=date.today())