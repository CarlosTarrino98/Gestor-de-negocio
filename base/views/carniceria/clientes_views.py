import json
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView
from django.http import JsonResponse
from base.forms import ClienteForm
from base.models import Cliente


class ClienteListView(TemplateView):
    template_name = 'carniceria/clientes/lista_clientes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener los clientes
        clientes = Cliente.objects.all()

        # Añadir los clientes al contexto
        context['clientes'] = clientes

        return context

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            accion = data.get('accion')
            cliente_id = data.get('cliente_id')

            if accion == 'eliminar_cliente' and cliente_id:
                cliente = get_object_or_404(Cliente, id=cliente_id)
                cliente.delete()
                return JsonResponse({'success': True, 'message': 'Cliente eliminado correctamente.'})

            return JsonResponse({'success': False, 'message': 'Acción no válida o cliente no encontrado.'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Error al procesar los datos JSON.'})


class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'carniceria/clientes/crear_cliente.html'
    success_url = reverse_lazy('lista_clientes')


class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'carniceria/clientes/editar_cliente.html'
    success_url = reverse_lazy('lista_clientes')

    def get_initial(self):
        initial = super().get_initial()
        cliente = self.get_object()
        return initial
