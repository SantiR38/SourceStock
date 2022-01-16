from django import forms
from datetime import date
from erp.functions import lista_proveedores, lista_clientes

CONDICIONES_IVA = [("Consumidor Final", "Consumidor Final"),
    ("Responsable Inscripto", "Responsable Inscripto"),
    ("Monotributista", "Monotributista"),
    ("IVA Excento", "IVA Excento"),
    ("No Alcanzado", "No Alcanzado"),
]


class FormBusqueda(forms.Form):
    buscar = forms.IntegerField(label="")


class FormVenta(forms.Form): # Sirve para la actualización inventario en general
    code = forms.IntegerField(label_suffix= "*:")
    quantity = forms.IntegerField(label_suffix= "*:")
    cliente = forms.ChoiceField(choices=lista_clientes, label= "Cliente", required=False, label_suffix= "**:")
    dni_cliente = forms.IntegerField(required=False, label="DNI Cliente", label_suffix= "**:")


class FormNuevoArticulo(forms.Form):
    code = forms.IntegerField(label_suffix= "*:")
    description = forms.CharField(required=False)
    is_in_dolar = forms.BooleanField(label="Cotiza en dolar", required=False)
    cost_no_taxes = forms.DecimalField(max_digits=10,
                                       decimal_places=2,
                                       label_suffix= "*:",
                                       label="Costo sin IVA",
                                       required=False)
    cost = forms.DecimalField(max_digits=10,
                               decimal_places=2,
                               label_suffix= "*:",
                               label="Costo con IVA",
                               required=False)
    profit_percentage = forms.DecimalField(max_digits=10, decimal_places=2, label_suffix= "*:")
    discount_percentage = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, label_suffix= "*:")
    section = forms.CharField(required=False)
    brand = forms.CharField(required=False)
    model = forms.CharField(required=False)
    stock = forms.IntegerField(label_suffix="*:")
    min_stock_allowed = forms.IntegerField(required=False, label="Stock mínimo permitido", initial=1,)


class FormEntrada(forms.Form):
    code = forms.IntegerField(label_suffix="*:")
    is_in_dolar = forms.BooleanField(label="Cotiza en dolar", required=False)
    cost_no_taxes = forms.DecimalField(max_digits=10, decimal_places=2,
        label="Costo sin IVA", label_suffix="**:", required=False)
    cost = forms.DecimalField(max_digits=10, decimal_places=2,
        label="Costo con IVA", label_suffix="**:", required=False)
    quantity = forms.IntegerField(label_suffix="*:")
    proveedor = forms.ChoiceField(choices=lista_proveedores, label="Proveedor",
        label_suffix="*:")
    fecha = forms.DateTimeField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}),
        label_suffix="*:", initial=date.today())

    def clean(self):
        cleaned_data = super().clean()
        if all(cleaned_data['cost'], cleaned_data['cost_no_taxes']):
            cleaned_data['inexistente'] = "PROBLEMA: Los campos cost final y " \
                "cost neto + IVA estan completados. Debes llenar solo uno de estos dos campos."
        if not any(cleaned_data['cost'], cleaned_data['cost_no_taxes']):
            cleaned_data['inexistente'] = "Debes rellenar uno de los dos costos."
        
        return cleaned_data


class FormCliente(forms.Form):
    name = forms.CharField(max_length=50,label= "Nombre o Empresa", label_suffix= "*:")
    tax_condition = forms.ChoiceField(choices=CONDICIONES_IVA, label= "Condición IVA", label_suffix= "*:")
    dni = forms.IntegerField(label= "DNI", required=False)
    cuit = forms.CharField(required=False)
    direction = forms.CharField(max_length=50, required=False)
    phone_number = forms.CharField(required=False)
    email = forms.EmailField(required=False)


class FormFiltroFecha(forms.Form):
    fecha_inicial = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), 
                                label_suffix= "*:",
                                initial=date.today())
    fecha_final = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), 
                                label_suffix= "*:",
                                initial=date.today())


class FormProveedor(forms.Form):
    name = forms.CharField(max_length=100, label= "Nombre Empresa", label_suffix= "*:")
    tax_condition = forms.ChoiceField(choices=CONDICIONES_IVA, label= "Condición IVA", label_suffix= "*:")
    cuit = forms.CharField(required=False)
    direction = forms.CharField(max_length=50, required=False)
    phone_number = forms.CharField(required=False)
    email = forms.EmailField(required=False)
