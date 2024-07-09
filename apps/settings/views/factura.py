from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView
from apps.products.models import Factura
from apps.settings.forms.factura import FacturaForm
from django.urls import reverse_lazy

class FacturaListView(LoginRequiredMixin, ListView):
    model = Factura
    template_name = 'factura/list/page.html' 
    context_object_name = 'Factura'
    paginate_by = 10

    def get_queryset(self):
        return Factura.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Factura List'
        return context
    
class FacturaUpdateView(LoginRequiredMixin, UpdateView):
    model = Factura
    form_class = FacturaForm
    template_name = 'factura/form/page.html'
    success_url = reverse_lazy('settings:factura')

    def get_queryset(self):
        return Factura.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Factura'
        context['submit_text'] = 'Update'
        return context