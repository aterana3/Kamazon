from django.views.generic import DetailView
from apps.products.models import Product

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail/page.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
