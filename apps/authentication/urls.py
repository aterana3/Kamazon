from django.urls import path
from .views import authentication

app_name = 'authentication'

urlpatterns = [
    path('register/', authentication.AuthRegisterView.as_view(), name='register'),
    path('login/', authentication.AuthLoginView.as_view(), name='login'),
    path("login/qr/", authentication.QRLoginView.as_view(), name='qr_login'),
    path('logout/', authentication.AuthLogoutView, name='logout'),
]