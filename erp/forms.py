from django import forms

class FormVenta(forms.Form): # Sirve para la actualización inventario en general
    codigo = forms.IntegerField()
    cantidad = forms.IntegerField()

class FormNuevoArticulo(forms.Form):
    codigo = forms.IntegerField()
    descripcion = forms.CharField(required=False)
    costo = forms.DecimalField(max_digits=10, decimal_places=2)
    porcentaje_ganancia = forms.DecimalField(max_digits=10, decimal_places=2)
    seccion = forms.CharField(required=False)

class FormEntrada(forms.Form):
    codigo = forms.IntegerField()
    costo = forms.DecimalField(max_digits=10, decimal_places=2)
    cantidad = forms.IntegerField()
    fecha = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))

class FormCliente(forms.Form):
    OPTIONS = [("CF", "Consumidor Final"),
               ("RI", "Responsable Inscripto"),
               ("MO", "Monotributista"),
               ("IE", "IVA Excento"),
               ("NA", "No Alcanzado"),
               ]

    nombre = forms.CharField(max_length=50, label= "Nombre*")
    apellido = forms.CharField(max_length=50, label= "Apellido*")
    condicion_iva = forms.ChoiceField(choices=OPTIONS, label= "Condición IVA*")
    dni = forms.IntegerField(label= "DNI*")
    cuit = forms.IntegerField(required=False)
    direccion = forms.CharField(max_length=50, required=False)
    telefono = forms.IntegerField(required=False)
    email = forms.EmailField(required=False)