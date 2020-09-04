from django import forms
from datetime import date
from erp.functions import lista_proveedores, lista_clientes

class FormBusqueda(forms.Form):
    buscar = forms.IntegerField(label="")

class FormVenta(forms.Form): # Sirve para la actualización inventario en general
    codigo = forms.IntegerField(label_suffix= "*:")
    cantidad = forms.IntegerField(label_suffix= "*:")
    cliente = forms.ChoiceField(choices=lista_clientes, label= "Cliente", required=False, label_suffix= "**:")
    dni_cliente = forms.IntegerField(required=False, label="DNI Cliente", label_suffix= "**:")

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
    porcentaje_descuento = forms.DecimalField(max_digits=10, decimal_places=2, initial=0, label_suffix= "*:")
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
    proveedor = forms.ChoiceField(choices=lista_proveedores, label= "Proveedor", label_suffix= "*:")
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

    nombre = forms.CharField(max_length=50,label= "Nombre o Empresa", label_suffix= "*:")
    condicion_iva = forms.ChoiceField(choices=OPTIONS, label= "Condición IVA", label_suffix= "*:")
    dni = forms.IntegerField(label= "DNI", required=False)
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

class FormProveedor(forms.Form):
    OPTIONS = [("Consumidor Final", "Consumidor Final"),
               ("Responsable Inscripto", "Responsable Inscripto"),
               ("Monotributista", "Monotributista"),
               ("IVA Excento", "IVA Excento"),
               ("No Alcanzado", "No Alcanzado"),
               ]

    nombre = forms.CharField(max_length=100, label= "Nombre Empresa", label_suffix= "*:")
    condicion_iva = forms.ChoiceField(choices=OPTIONS, label= "Condición IVA", label_suffix= "*:")
    cuit = forms.CharField(required=False)
    direccion = forms.CharField(max_length=50, required=False)
    telefono = forms.CharField(required=False)
    email = forms.EmailField(required=False)