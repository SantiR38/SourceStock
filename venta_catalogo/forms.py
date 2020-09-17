from django import forms

class FormFiltrarArticulos(forms.Form):
    codigo = forms.IntegerField(required=False, label="Código")
    descripcion = forms.CharField(max_length=150, required=False, label="Descripción")
    seccion = forms.CharField(max_length=150, required=False, label="Sección")
    marca = forms.CharField(max_length=150, required=False)

class FormBuscarCliente(forms.Form):
    nombre = forms.CharField(max_length=50, required=False)
    dni = forms.IntegerField(required=False)

class FormDescuentoAdicional(forms.Form):
    descuento = forms.DecimalField(initial=0, max_digits=10, decimal_places=2, label_suffix= "*:")
