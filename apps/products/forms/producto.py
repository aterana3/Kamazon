from django import forms
from apps.products.models import Producto, Categoria

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['name', 'description', 'precio', 'stock', 'categoria']
        exclude = ['created_at', 'created_by', 'updated_at', 'updated_by']	
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
        }

    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
