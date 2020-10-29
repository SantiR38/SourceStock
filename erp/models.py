from django.db import models
from datetime import date
from decimal import Decimal

from django.shortcuts import redirect

def porcentaje_ganancia(costo, porcentaje):
    # Calcula el porcentaje de ganancia mediante los dos parámetros solicitados.
    precio_final = costo + (costo * porcentaje / 100)
    return precio_final

# *1: CASCADE, significa que cuando se borre un artículo de la tabla padre, el artículo de la
#     tabla hija que tiene esa clave foranea, también se borra

# *2: SET_NULL, cuando se borra el artículo, la tabla hija pone null como clave foranea.

class Article(models.Model):
    codigo = models.BigIntegerField(unique=True)
    descripcion = models.CharField(max_length=100, null=True)
    costo_sin_iva = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    porcentaje_ganancia = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    precio_sin_iva = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    porcentaje_descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    precio_descontado = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    seccion = models.CharField(max_length=100, blank=True) # blank=True hace que el valor vacio no se guarde como None, sino como ''.
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    stock = models.IntegerField(verbose_name="Cantidad")
    alarma_stock = models.IntegerField(verbose_name="Stock minimo permitido", null=True)
    id_state = models.ForeignKey('ArtState', on_delete=models.SET_NULL, null=True)
    en_dolar = models.BooleanField(default=False, null=True) # Determina si la cotización del producto es en dolar.

    @classmethod
    def get_context(cls, infForm):
        costo_sin_iva = infForm['costo_sin_iva']
        costo = infForm['costo']
        porcentaje_descuento = infForm['porcentaje_descuento']
        precio_descontado = None
        if costo_sin_iva is not None:
            costo = porcentaje_ganancia(costo_sin_iva, 21)
        elif costo is not None:
            costo_sin_iva = costo / Decimal(1.21)

        precio = porcentaje_ganancia(costo, infForm['porcentaje_ganancia'])

        if porcentaje_descuento is not None:
            precio_descontado = porcentaje_ganancia(precio, -porcentaje_descuento)

        context = {
            "codigo": infForm['codigo'],
            "descripcion": infForm['descripcion'],
            "costo_sin_iva": costo_sin_iva,
            "costo": costo,
            "precio_sin_iva": porcentaje_ganancia(costo_sin_iva, infForm['porcentaje_ganancia']),
            "precio": precio,
            "porcentaje_ganancia": infForm['porcentaje_ganancia'],
            "porcentaje_descuento": porcentaje_descuento,
            "precio_descontado": precio_descontado,
            "seccion": infForm['seccion'],
            "marca": infForm['marca'],
            "modelo": infForm['modelo'],
            "stock": infForm['stock'],
            "alarma_stock": infForm['alarma_stock'],
            "en_dolar": infForm['en_dolar']
        }

        return context

    @classmethod
    def create_new(cls, infForm):
        article = cls.objects.filter(codigo=infForm['codigo'])
        if article.exists():
            mensaje = "El código ya está siendo utilizado por otro producto."
        else:
            if infForm['costo'] is not None and infForm['costo_sin_iva'] is not None:
                mensaje = "PROBLEMA: Los campos costo final y costo neto + IVA estan completados. Debes llenar solo uno de estos dos campos."
            elif infForm['costo'] is not None or infForm['costo_sin_iva'] is not None:
                cls.objects.create(codigo=cls.get_context(infForm)['codigo'],
                                        descripcion=cls.get_context(infForm)['descripcion'],
                                        costo_sin_iva=cls.get_context(infForm)['costo_sin_iva'],
                                        costo=cls.get_context(infForm)['costo'],
                                        en_dolar=cls.get_context(infForm)['en_dolar'],
                                        precio_sin_iva=cls.get_context(infForm)['precio_sin_iva'],
                                        precio=cls.get_context(infForm)['precio'],
                                        porcentaje_ganancia=cls.get_context(infForm)['porcentaje_ganancia'],
                                        porcentaje_descuento=cls.get_context(infForm)['porcentaje_descuento'],
                                        precio_descontado=cls.get_context(infForm)['precio_descontado'],
                                        seccion=cls.get_context(infForm)['seccion'],
                                        marca=cls.get_context(infForm)['marca'],
                                        modelo=cls.get_context(infForm)['modelo'],
                                        stock=cls.get_context(infForm)['stock'],
                                        alarma_stock=cls.get_context(infForm)['alarma_stock'])
                mensaje = "Artículo agregado exitosamente"
            else:
                mensaje = "PROBLEMA: Debes rellenar uno de los dos costos."
        return mensaje

    def __str__(self):
        return self.descripcion


class ArtState(models.Model): # Tiene solo 3 filas: 1. Active; 2. Inactive, 3. Deleted.
    nombre = models.CharField(max_length=10)

    @classmethod
    def add_art_state(cls):
        # Esta función es utilizada apenas se lanza el proyecto para registrar los tres campos de ArtState.
        cls.objects.create(nombre="Active")
        cls.objects.create(nombre="Inactive")
        cls.objects.create(nombre="Deleted")

    def __str__(self):
        return self.nombre


class Perdida(models.Model):
    fecha = models.DateField()
    id_state = models.ForeignKey('ArtState', on_delete=models.SET_NULL, null=True) # *2
    total = models.DecimalField(max_digits=10, decimal_places=2)


class DetallePerdida(models.Model):
    id_perdida = models.ForeignKey('Perdida', on_delete=models.CASCADE) # *1
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    id_producto = models.ForeignKey('Article', on_delete=models.SET_NULL, null=True) # *2
    cantidad = models.IntegerField()


class Venta(models.Model):
    fecha = models.DateField()
    id_state = models.ForeignKey('ArtState', on_delete=models.SET_NULL, null=True) # *2
    total = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    descuento_adicional = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_con_descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True)

    @classmethod
    def crear_venta_vacia(cls, estado):
        venta = cls(fecha=date.today(),
                    total=0,
                    id_state=estado,
                    descuento=0,
                    descuento_adicional=0)
        venta.save()
        return venta
    
    @classmethod
    def get_active(cls):
        return Venta.objects.get(id_state=ArtState.objects.get(nombre="Active"))
    
    @classmethod
    def get_inactive(cls):
        """
        Muestra las últimas 50 ventas realizadas
        """
        estado = ArtState.objects.get(nombre="Inactive")
        return cls.objects.filter(id_state=estado).order_by('-fecha', '-id')[:50] 


class DetalleVenta(models.Model):
    id_venta = models.ForeignKey('Venta', on_delete=models.CASCADE) # *1
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # Si bien tanto este dato como el del precio estan en el objeto Article,
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # es mejor guardar el producto al precio que se vendió para mejor contabilidad
    precio_por_cantidad = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    porcentaje_descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    id_producto = models.ForeignKey('Article', on_delete=models.SET_NULL, null=True) # *2
    cantidad = models.IntegerField()

    @classmethod
    def take_product_back(cls, param):
        products = cls.objects.filter(id_venta=param)
        for i in products:
            if i.id_producto.stock >= i.cantidad:
                i.id_producto.stock += i.cantidad
                i.id_producto.save()


class Entrada(models.Model):
    fecha = models.DateField()
    id_state = models.ForeignKey('ArtState', on_delete=models.SET_NULL, null=True) # *2
    total = models.DecimalField(max_digits=10, decimal_places=2)
    proveedor = models.ForeignKey('Proveedor', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return '%s (%s)' % (self.fecha, self.id)
    
    @classmethod
    def get_inactive(cls):
        """
        Muestra las últimas 50 compras realizadas
        """
        estado = ArtState.objects.get(nombre="Inactive")
        return cls.objects.filter(id_state=estado).order_by('-fecha', '-id')[:50] 


class DetalleEntrada(models.Model):
    id_entrada = models.ForeignKey('Entrada', on_delete=models.CASCADE) # *1
    en_dolar = models.BooleanField(default=False, null=True)
    costo_sin_iva = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    id_producto = models.ForeignKey('Article', on_delete=models.SET_NULL, null=True) # *2
    cantidad = models.IntegerField()

    @classmethod
    def give_product_back(cls, param):
        products = cls.objects.filter(id_entrada=param)
        for i in products:
            if i.id_producto.stock >= i.cantidad:
                i.id_producto.stock -= i.cantidad
                i.id_producto.save()


class Cliente(models.Model):
    nombre = models.CharField(max_length=50)
    condicion_iva = models.CharField(max_length=25, default="Consumidor Final")
    dni = models.PositiveIntegerField(null=True)
    cuit = models.CharField(max_length=15, null=True)
    direccion = models.CharField(max_length=50, null=True)
    telefono = models.CharField(max_length=30, null=True)
    email = models.EmailField(null=True)


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    condicion_iva = models.CharField(max_length=25)
    cuit = models.CharField(max_length=15, null=True)
    direccion = models.CharField(max_length=50, null=True)
    telefono = models.CharField(max_length=30, null=True)
    email = models.EmailField(null=True)