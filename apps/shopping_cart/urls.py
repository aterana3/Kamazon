from django.urls import path
from apps.shopping_cart.views import shopping_cart

app_name = 'shopping_cart'

urlpatterns = [
    #path('', shopping_cart.ShoppingCart.as_view(), name='shopping_cart'),
    path('ia', shopping_cart.ShoppingCartIA.as_view(), name='ia'),
]