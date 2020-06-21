from django.db import models

# Create your models here.

class Article(models.Model):
    codigo = models.BigIntegerField(unique=True)
    descripcion = models.CharField(max_length=100, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
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


class DetalleVenta(models.Model):
    id_venta = models.ForeignKey('Venta', on_delete=models.CASCADE) # *1
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    id_producto = models.ForeignKey('Article', on_delete=models.SET_NULL, null=True) # *2
    cantidad = models.IntegerField()


class Entrada(models.Model):
    fecha = models.DateField()
    id_state = models.ForeignKey('ArtState', on_delete=models.SET_NULL, null=True) # *2
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return '%s (%s)' % (self.fecha, self.id)


class DetalleEntrada(models.Model):
    id_entrada = models.ForeignKey('Entrada', on_delete=models.CASCADE) # *1
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    id_producto = models.ForeignKey('Article', on_delete=models.SET_NULL, null=True) # *2
    cantidad = models.IntegerField()


    # *1: CASCADE, significa que cuando se borre un artículo de la tabla padre, el artículo de la
    #     tabla hija que tiene esa clave foranea, también se borra

    # *2: SET_NULL, cuando se borra el artículo, la tabla hija pone null como clave foranea.