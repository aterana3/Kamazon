from django.urls import path
from .views import device, user, product

app_name = 'settings'

urlpatterns = [
    path('devices/', device.DeviceListView.as_view(), name='devices'),
    path('devices/<int:device_id>/close_session/', device.ForceLogoutView.as_view(), name='device_close_session'),
    path('devices/form/', device.QRScanView.as_view(), name='device_add'),
    path('devices/send_message/', device.sendMessageDevice.as_view(), name='device_send_message'),

    path('profile/', user.UserDetailView.as_view(), name='profile'),
    path('profile/update/', user.UserUpdateView.as_view(), name='profile_update'),

    path('products/', product.ProductListView.as_view(), name='products'),
    path('products/create/', product.ProductCreateView.as_view(), name='product_create'),
]