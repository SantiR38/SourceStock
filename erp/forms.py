from django import forms

class FormBusqueda(forms.Form):
    buscar = forms.IntegerField()

class FormVenta(forms.Form): # Sirve para la actualización inventario en general
    codigo = forms.IntegerField(label_suffix= "*:")
    cantidad = forms.IntegerField(label_suffix= "*:")

class FormNuevoArticulo(forms.Form):
    codigo = forms.IntegerField(label_suffix= "*:")
    descripcion = forms.CharField(required=False)
    costo = forms.DecimalField(max_digits=10, decimal_places=2, label_suffix= "*:")
    porcentaje_ganancia = forms.DecimalField(max_digits=10, decimal_places=2, label_suffix= "*:")
    seccion = forms.CharField(required=False)
    stock = forms.IntegerField(label_suffix= "*:")

class FormEntrada(forms.Form):
    codigo = forms.IntegerField(label_suffix= "*:")
    costo = forms.DecimalField(max_digits=10, decimal_places=2, label_suffix= "*:")
    cantidad = forms.IntegerField(label_suffix= "*:")
    fecha = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), label_suffix= "*:")

class FormCliente(forms.Form):
    OPTIONS = [("CF", "Consumidor Final"),
               ("RI", "Responsable Inscripto"),
               ("MO", "Monotributista"),
               ("IE", "IVA Excento"),
               ("NA", "No Alcanzado"),
               ]

    nombre = forms.CharField(max_length=50, label_suffix= "*:")
    apellido = forms.CharField(max_length=50, label_suffix= "*:")
    condicion_iva = forms.ChoiceField(choices=OPTIONS, label= "Condición IVA", label_suffix= "*:")
    dni = forms.IntegerField(label= "DNI", label_suffix= "*:")
    cuit = forms.IntegerField(required=False)
    direccion = forms.CharField(max_length=50, required=False)
    telefono = forms.IntegerField(required=False)
    email = forms.EmailField(required=False)