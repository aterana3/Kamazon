from django import forms
from models import Reseña

class ReseñaForm(forms.ModelForm):
    class Meta:
        model = Reseña
        fields = ['título', 'contenido', 'valoración', 'autor', 'imagen']