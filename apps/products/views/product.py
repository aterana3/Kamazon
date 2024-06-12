from django.urls import reverse_lazy
from apps.products.forms.producto import ProductoForm
from apps.products.models import Producto
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.db.models import Q

class ProductoListView(ListView):
    model = Producto
    template_name = 'productos/list.html'
    context_object_name = 'productos'
    permission_required = "view_producto"

    def get_queryset(self):
        self.query = Q()
        q1 = self.request.GET.get('q1')
        if q1 is not None:
            self.query.add(Q(name__icontains=q1), Q.AND)
        return self.model.objects.filter(self.query).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Productos'
        context['create_url'] = reverse_lazy('products:producto_create')
        context['permissions'] = self.request.session.get('permissions', {})
        context['permission_add'] = context['permissions'].get('add_producto', '')
        return context

class ProductoCreateView(CreateView):
    model = Producto
    template_name = 'productos/form.html'
    form_class = ProductoForm
    success_url = reverse_lazy('products:producto_list')
    permission_required = "add_producto"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Grabar Categoria'
        context['back_url'] = self.success_url
        return context

class ProductoUpdateView(UpdateView):
    model = Producto
    template_name = 'productos/form.html'
    form_class = ProductoForm
    success_url = reverse_lazy('products:producto_list')
    permission_required = "change_producto"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Actualizar producto'
        context['back_url'] = self.success_url
        return context

class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = 'productos/delete.html'
    success_url = reverse_lazy('products:producto_list')
    permission_required = "delete_producto"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Eliminar producto'
        context['description'] = f"¿Desea Eliminar el producto: {self.object.name}?"
        context['back_url'] = self.success_url
        return context
