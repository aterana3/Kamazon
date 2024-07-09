from django.urls import path
from .views import device, user, product, factura

app_name = 'settings'

urlpatterns = [
    path('devices/', device.DeviceListView.as_view(), name='devices'),
    path('devices/<int:device_id>/close_session/', device.ForceLogoutView.as_view(), name='device_close_session'),
    path('devices/add/', device.QRScanView.as_view(), name='device_add'),
    path('devices/authorize/', device.SendMessageDevice.as_view(), name='device_authorize'),

    path('profile/', user.UserDetailView.as_view(), name='profile'),
    path('profile/update/', user.UserUpdateView.as_view(), name='profile_update'),

    path('products/', product.ProductListView.as_view(), name='products'),
    path('products/create/', product.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/update/', product.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', product.ProductDeleteView.as_view(), name='product_delete'),

    path('factura/', factura.FacturaListView.as_view(), name='factura'),
    path('factura/<int:pk>/update/', factura.FacturaUpdateView.as_view(), name='factura_update'),
]