from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.products.models import Factura
from django_ckeditor_5.widgets import CKEditor5Widget

User = get_user_model()

class FacturaForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False

    class Meta:
        model = Factura
        fields = '__all__'
        exclude = ['user', 'updated_at']
        widgets = {
            "description": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            )
        }

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get("price")
        stock = cleaned_data.get("stock")

        if price < 0:
            raise ValidationError("The price must be greater than or equal to zero.")

        if stock < 0:
            raise ValidationError("The stock must be greater than or equal to zero.")

        return cleaned_data