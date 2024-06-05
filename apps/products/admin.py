from django.contrib import admin

from apps.products.models import Producto, Categoria
admin.site.register(Producto)
admin.site.register(Categoria)
