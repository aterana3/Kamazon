from django.urls import path
from .views import product

app_name = 'products'
# urlpatterns = []
urlpatterns = [
    path('producto/list', product.ProductoListView.as_view(),name="producto_list"),
    path('producto/create',ProductoCreateView.as_view(),name="producto_create"),
    path('producto/update/<int:pk>',ProductoUpdateView.as_view() ,name="producto_update"),
    path('producto/delete/<int:pk>',ProductoDeleteView.as_view() ,name="producto_delete"),
]