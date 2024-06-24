from django.urls import path
from kamazon.consumers.qrcode import QRConsumer
from kamazon.consumers.product import ProductConsumer

websocket_urlpatterns = [
    path("ws/qr/<str:token>/", QRConsumer.as_asgi()),
    path("ws/product/<str:token>/", ProductConsumer.as_asgi()),
]