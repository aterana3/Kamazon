from django.urls import path
from .views import invoice

app_name = 'invoice'

urlpatterns = [
    path('create', invoice.InvoiceCreateView.as_view(), name='invoice_create'),
]