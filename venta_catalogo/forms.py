from django import forms

class FormFiltrarArticulos(forms.Form):
    code = forms.IntegerField(required=False, label="Código")
    description = forms.CharField(max_length=150, required=False, label="Descripción")
    section = forms.CharField(max_length=150, required=False, label="Sección")
    brand = forms.CharField(max_length=150, required=False)

class FormBuscarCliente(forms.Form):
    nombre = forms.CharField(max_length=50, required=False)
    dni = forms.IntegerField(required=False)

class FormDescuentoAdicional(forms.Form):
    descuento = forms.DecimalField(initial=0, max_digits=10, decimal_places=2, label_suffix= "*:", label="Porcentaje de descuento")
