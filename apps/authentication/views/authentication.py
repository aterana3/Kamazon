from django.views.generic import CreateView
from apps.authentication.forms.register import RegisterForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from apps.authentication.forms.login import LoginForm
import uuid
from django.core.cache import cache
from kamazon.fuctions import generate_qrcode
from django.views import View
import json
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect

class AuthRegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'register/page.html'
    success_url = reverse_lazy('auth:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register'
        context['submit_text'] = 'Register'
        return context
    
class AuthLoginView(LoginView):
    template_name = 'login/page.html'
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        token = str(uuid.uuid4())
        cache.set(token, {'status': 'pending'}, timeout=600)
        qr_data = {'token': token}
        qr_code_image = generate_qrcode(qr_data)

        context['title'] = 'Login'
        context['submit_text'] = 'Login'
        context['qr_code_image'] = qr_code_image
        context['token'] = token
        return context
    
class QRLoginView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        session_key = data['session_key']
        token = data['token']
        try:
            session = Session.objects.get(session_key=session_key)
        except Session.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid session key'}, status=400)
        if session.expire_date < timezone.now():
            return JsonResponse({'success': False, 'message': 'Session has expired'}, status=400)
        user_id = session.get_decoded().get('_auth_user_id')
        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid user'}, status=400)
        login(request, user)
        cache.delete(token)
        return JsonResponse({'success': True, 'message': 'Login successful'})
    
@login_required
def AuthLogoutView(request):
    logout(request)
    return redirect('home')
