from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import ReseñaForm
from .models import Reseña

class ReseñaCreateView(CreateView):
    model = Reseña
    template_name = 'reseñas/reseña_form.html'
    form_class = ReseñaForm
    success_url = reverse_lazy('ruta_a_tu_lista_de_reseñas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Reseña'
        return context

    def form_valid(self, form):
        form.instance.producto_id = self.kwargs['id_producto']  # Assuming you are passing 'id_producto' in URL
        return super().form_valid(form)
