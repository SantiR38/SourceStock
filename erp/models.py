from django.db import models

# Create your models here.

class Article(models.Model):
    codigo = models.BigIntegerField(unique=True)
    descripcion = models.CharField(max_length=100, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    seccion = models.CharField(max_length=100, blank=True, null=True)
    stock = models.IntegerField(verbose_name="Cantidad")
    id_state = models.ForeignKey('Art_State', on_delete=models.CASCADE)

    def __str__(self):
        return 'Artículo: %s  -  Precio: %s' % (self.descripcion, self.precio)

# WARNING: Before making the migrations, translate all the models to english!!

class ArtState(models.Model):
    nombre = models.CharField(max_length=10)

class Perdida(models.Model):
    fecha = models.DateTimeField()
    id_state = models.ForeignKey('Art_State', on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)

class DetallePerdida():
    id_perdida = models.ForeignKey('Perdida', on_delete=models.CASCADE)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    id_producto = models.ForeignKey('Article', on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()


class Venta(models.Model):
    fecha = models.DateTimeField()
    id_state = models.ForeignKey('Art_State', on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)

class DetalleVenta():
    id_venta = models.ForeignKey('Venta', on_delete=models.CASCADE)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    id_producto = models.ForeignKey('Article', on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()


class Entrada(models.Model):
    fecha = models.DateTimeField()
    id_state = models.ForeignKey('Art_State', on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)


class DetalleEntrada():
    id_entrada = models.ForeignKey('Entrada', on_delete=models.CASCADE)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    id_producto = models.ForeignKey('Article', on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()