from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.http import JsonResponse
from base.models import Inventario

class InventarioListView(LoginRequiredMixin, ListView):
    model = Inventario
    template_name = 'asador/inventario/lista_inventario.html'
    context_object_name = 'inventarios'

    # Configuración de LoginRequiredMixin
    login_url = 'login'
    redirect_field_name = None

    def post(self, request, *args, **kwargs):
        if request.POST.get('accion') == 'eliminar':
            inventario_id = request.POST.get('inventario_id')
            if inventario_id:
                inventario = get_object_or_404(Inventario, id=inventario_id)
                inventario.delete()
                return JsonResponse({'success': True, 'message': 'Inventario eliminado correctamente.'})
        return super().get(request, *args, **kwargs)

class InventarioCreateView(CreateView):
    model = Inventario
    template_name = 'asador/inventario/crear_inventario.html'
    fields = ['producto', 'cantidad_disponible'] 
    success_url = reverse_lazy('lista_inventario')

class InventarioUpdateView(UpdateView):
    model = Inventario
    template_name = 'asador/inventario/editar_inventario.html'
    fields = ['producto', 'cantidad_disponible'] 
    success_url = reverse_lazy('lista_inventario')
