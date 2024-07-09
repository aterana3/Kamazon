from django.urls import path
from .views import device, user, product, invoice

app_name = 'settings'

urlpatterns = [
    path('devices/', device.DeviceListView.as_view(), name='devices'),
    path('devices/<int:device_id>/close_session/', device.ForceLogoutView.as_view(), name='device_close_session'),
    path('devices/scan/', device.QRScanView.as_view(), name='device_scan'),
    path('devices/authorize/', device.SendMessageDevice.as_view(), name='device_authorize'),

    path('profile/', user.UserDetailView.as_view(), name='profile'),
    path('profile/update/', user.UserUpdateView.as_view(), name='profile_update'),

    path('products/', product.ProductListView.as_view(), name='products'),
    path('products/create/', product.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/update/', product.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', product.ProductDeleteView.as_view(), name='product_delete'),

    path('invoices/', invoice.InvoiceListView.as_view(), name='invoices'),
    path('invoices/<int:pk>/detail/', invoice.InvoiceDetailView.as_view(), name='invoice_detail'),
]