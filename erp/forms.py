from django import forms

class FormVenta(forms.Form): # Sirve también para la actualización de compra
    codigo = forms.IntegerField()
    cantidad = forms.IntegerField()

class FormNuevoArticulo(forms.Form):
    codigo = forms.IntegerField()
    descripcion = forms.CharField(required=False)
    costo = forms.DecimalField(max_digits=10, decimal_places=2)
    precio = forms.DecimalField(max_digits=10, decimal_places=2)
    seccion = forms.CharField(required=False)

class FormEntrada(forms.Form):
    codigo = forms.IntegerField()
    costo = forms.DecimalField(max_digits=10, decimal_places=2)
    cantidad = forms.IntegerField()
    fecha = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))