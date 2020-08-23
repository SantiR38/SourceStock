from django.db import models

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
    seccion = models.CharField(max_length=100, blank=True, null=True)
    stock = models.IntegerField(verbose_name="Cantidad")
    id_state = models.ForeignKey('ArtState', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.descripcion


class ArtState(models.Model): # Tiene solo 3 filas: 1. Active; 2. Inactive, 3. Deleted.
    nombre = models.CharField(max_length=10)

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
    cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True)


class DetalleVenta(models.Model):
    id_venta = models.ForeignKey('Venta', on_delete=models.CASCADE) # *1
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # Si bien tanto este dato como el del precio estan en el objeto Article,
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # es mejor guardar el producto al precio que se vendió para mejor contabilidad
    id_producto = models.ForeignKey('Article', on_delete=models.SET_NULL, null=True) # *2
    cantidad = models.IntegerField()


class Entrada(models.Model):
    fecha = models.DateField()
    id_state = models.ForeignKey('ArtState', on_delete=models.SET_NULL, null=True) # *2
    total = models.DecimalField(max_digits=10, decimal_places=2)
    proveedor = models.ForeignKey('Proveedor', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return '%s (%s)' % (self.fecha, self.id)


class DetalleEntrada(models.Model):
    id_entrada = models.ForeignKey('Entrada', on_delete=models.CASCADE) # *1
    costo_sin_iva = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    id_producto = models.ForeignKey('Article', on_delete=models.SET_NULL, null=True) # *2
    cantidad = models.IntegerField()


class Cliente(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50, null=True)
    condicion_iva = models.CharField(max_length=25)
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