from django.forms import ModelForm
from apps.products.models import Categoria

class CategoriaForm(ModelForm):
    class Meta:
        model = Categoria
        fields = '_all_'
        exclude = ['created_at', 'created_by', 'updated_at', 'update_by']
