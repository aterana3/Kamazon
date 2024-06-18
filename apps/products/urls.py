from django.urls import path
from .views import products

app_name = 'products'

urlpatterns = [
    #path('', products.ProductListView.as_view(), name='products'),
    path('<int:pk>/', products.ProductDetailView.as_view(), name='product_detail'),
]