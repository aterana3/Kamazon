from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from apps.products.models import Product

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/list/page.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Products'
        return context