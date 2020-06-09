from django.db import models

# Create your models here.

class Article(models.Model):
    codigo = models.BigIntegerField(unique=True)
    descripcion = models.CharField(max_length=100, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    seccion = models.CharField(max_length=100, blank=True, null=True)
    stock = models.IntegerField(verbose_name="Cantidad")

    def __str__(self):
        return 'Artículo: %s  -  Precio: %s' % (self.descripcion, self.precio)