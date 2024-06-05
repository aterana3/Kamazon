from django.urls import reverse_lazy
from apps.products.forms.producto import ProductoForm
from apps.products.models import Categoria
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.db.models import Q

class ProductoListView(ListView):
    model = Categoria
    template_name = 'categorias/list.html'
    context_object_name = 'categorias'
    permission_required = "view_categoria"

    def get_queryset(self):
        self.query = Q()
        q1 = self.request.GET.get('q1')
        if q1 is not None:
            self.query.add(Q(name__icontains=q1), Q.AND)
        return self.model.objects.filter(self.query).order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Categorias'
        context['create_url'] = reverse_lazy('products:categoria_create')
        context['permissions'] = self.request.session.get('permissions', {})
        context['permission_add'] = context['permissions'].get('add_categoria', '')
        return context

class ProductoCreateView(CreateView):
    model = Categoria
    template_name = 'categorias/form.html'
    form_class = ProductoForm
    success_url = reverse_lazy('products:categoria_list')
    permission_required = "add_producto"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Grabar Categoria'
        context['back_url'] = self.success_url
        return context

class ProductoUpdateView(UpdateView):
    model = Categoria
    template_name = 'categorias/form.html'
    form_class = ProductoForm
    success_url = reverse_lazy('products:categoria_list')
    permission_required = "change_producto"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Actualizar categoria'
        context['back_url'] = self.success_url
        return context

class ProductoDeleteView(DeleteView):
    model = Categoria
    template_name = 'categorias/delete.html'
    success_url = reverse_lazy('products:categoria_list')
    permission_required = "delete_producto"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grabar'] = 'Eliminar la categoria'
        context['description'] = f"¿Desea Eliminar la categoria: {self.object.name}?"
        context['back_url'] = self.success_url
        return context
