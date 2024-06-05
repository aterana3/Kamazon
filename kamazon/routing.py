from django.urls import path
from kamazon.consumers import QRConsumer

websocket_urlpatterns = [
    path("ws/qr/<str:token>/", QRConsumer.as_asgi()),
]