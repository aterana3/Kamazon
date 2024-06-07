from django.urls import path
from .views import ReseñaCreateView

urlpatterns = [
    path('producto/<int:id_producto>/crear_reseña/', ReseñaCreateView.as_view(), name='crear_reseña'),
]
