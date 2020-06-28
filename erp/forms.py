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
    porcentaje_ganancia = forms.DecimalField(max_digits=10, decimal_places=2)
    cantidad = forms.IntegerField()
    fecha = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))