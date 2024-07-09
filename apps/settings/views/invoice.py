from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView
from apps.products.models import Invoice
from apps.settings.forms.invoice import InvoiceForm
from django.urls import reverse_lazy


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'invoice/list/page.html'
    context_object_name = 'invoice'
    paginate_by = 10

    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Invoice List'
        return context


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoice/form/page.html'
    success_url = reverse_lazy('settings:invoice')

    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Invoice'
        context['submit_text'] = 'Update'
        return context