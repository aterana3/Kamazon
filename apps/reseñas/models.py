from django.db import models
from django.conf import settings



class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    
class Reseña(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='reseñas')
    título = models.CharField(max_length=100)
    contenido = models.TextField()
    STAR_CHOICES = [
        (1, 'Una estrella - No me gustó en absoluto'),
        (2, 'Dos estrellas - No me gustó'),
        (3, 'Tres estrellas - Está bien'),
        (4, 'Cuatro estrellas - Me gustó'),
        (5, 'Cinco estrellas - Me encantó'),
    ]
    valoración = models.PositiveIntegerField(choices=STAR_CHOICES)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reseñas')    
    fecha = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='reseñas_imagenes/', blank=True, null=True)


    def __str__(self):
        return f"{self.título} - {self.producto.nombre}"
