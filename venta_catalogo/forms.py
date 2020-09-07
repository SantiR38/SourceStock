from django import forms

class FormFiltrarArticulos(forms.Form):
    codigo = forms.IntegerField(required=False)
    seccion = forms.CharField(max_length=150, required=False)
    marca = forms.CharField(max_length=150, required=False)