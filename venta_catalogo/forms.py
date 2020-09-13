from django import forms

class FormFiltrarArticulos(forms.Form):
    codigo = forms.IntegerField(required=False, label="Código")
    descripcion = forms.CharField(max_length=150, required=False, label="Descripción")
    seccion = forms.CharField(max_length=150, required=False, label="Sección")
    marca = forms.CharField(max_length=150, required=False)

class FormBuscarCliente(forms.Form):
    nombre = forms.CharField(max_length=50, required=False)
    dni = forms.IntegerField(required=False)