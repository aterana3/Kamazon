from django.db import models
from django.forms import model_to_dict

class Producto(models.Model):
    name = models.CharField(verbose_name='Nombre de los productos', max_length=50, unique=True)
    description = models.TextField(verbose_name="Descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    stock = models.PositiveIntegerField(verbose_name='Stock disponible', default=0)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_model_to_dict(self):
        item=model_to_dict(self)
        return item


    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'
        ordering = ['-name']


class Categoria(models.Model):
    name = models.CharField(verbose_name='Nombre de la categoría', max_length=50, unique=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'
        ordering = ['-name']
# Create your models here.
