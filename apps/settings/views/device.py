from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from apps.core.models import Device
from django.views import View
from django.contrib.sessions.models import Session
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
import json
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

class DeviceListView(LoginRequiredMixin, ListView):
    model = Device
    template_name = 'devices/list/page.html'
    context_object_name = 'devices'
    paginate_by = 10

    def get_queryset(self):
        return Device.objects.filter(user=self.request.user).order_by('-last_activity')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_device_session_key = self.request.session.session_key
        current_device = Device.objects.filter(session__session_key=current_device_session_key).first()
        context['title'] = 'Devices'
        context['current_device'] = current_device
        return context

class ForceLogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        device_id = kwargs.get('device_id')
        device = Device.objects.get(id=device_id)
        if device.user == request.user:
            Session.objects.filter(session_key=device.session.session_key).delete()
            device.delete()
        return redirect(reverse_lazy('settings:devices'))

class QRScanView(LoginRequiredMixin, TemplateView):
    template_name = 'devices/add/page.html'

class SendMessageDevice(LoginRequiredMixin, View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            if not data:
                raise KeyError("data is missing")

            token = data['token']
            cache_data = cache.get(token)

            if cache_data is None:
                return JsonResponse({'success': False, 'message': 'Invalid token'}, status=400)

            user_id = request.user.id
            cache_data['user_id'] = user_id
            cache.set(token, cache_data, timeout=600)

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                token,
                {
                    'type': 'handle_receive',
                    'user_id': user_id
                }
            )
            return JsonResponse({'success': True, 'message': 'Message sent'})
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
        except KeyError as e:
            print(f"Error: {e}")
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
