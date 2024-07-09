from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class ShoppingCartIA(LoginRequiredMixin, TemplateView):
    template_name = 'ia/index.html'