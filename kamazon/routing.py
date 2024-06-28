from django.urls import path
from kamazon.consumers.qrcode import QRConsumer
from kamazon.consumers.product import ProductTrainingConsumer, ProductDetectorConsumer


websocket_urlpatterns = [
    path("ws/qr/<str:token>/", QRConsumer.as_asgi()),
    path("ws/product/training/<str:token>/", ProductTrainingConsumer.as_asgi()),
    path("ws/product/detect/<int:user_id>/", ProductDetectorConsumer.as_asgi()),
]