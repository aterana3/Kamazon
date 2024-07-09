from django.urls import path
from .views import products

app_name = 'products'

urlpatterns = [
    path('', products.ProductListView.as_view(), name='products_list'),
    path('<int:pk>/', products.ProductDetailView.as_view(), name='product_detail'),
    path('fetch/<int:pk>/', products.ProductDetailFetchView.as_view(), name='product_fetch'),
]