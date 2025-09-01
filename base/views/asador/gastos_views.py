from datetime import datetime, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.http import JsonResponse
from base.forms import GastoForm
from base.models import Gasto
from django.utils.timezone import make_aware

class GastoListView(LoginRequiredMixin, ListView):
    model = Gasto
    template_name = 'asador/gastos/lista_gastos.html'
    context_object_name = 'gastos'
    ordering = ['fecha']

    # Configuración de LoginRequiredMixin
    login_url = 'login'
    redirect_field_name = None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener las fechas de los parámetros GET
        fecha_inicio_str = self.request.GET.get('fecha_inicio')
        fecha_fin_str = self.request.GET.get('fecha_fin')

        if fecha_inicio_str and fecha_fin_str:
            try:
                # Convertir las fechas a objetos datetime
                fecha_inicio = make_aware(datetime.strptime(fecha_inicio_str, '%Y-%m-%d'))
                fecha_fin = make_aware(datetime.strptime(fecha_fin_str, '%Y-%m-%d')) + timedelta(days=1) - timedelta(seconds=1)
            except ValueError:
                fecha_inicio, fecha_fin = None, None
        else:
            # Si no hay fechas, usar la semana actual
            hoy = datetime.now().date()
            fecha_inicio = hoy - timedelta(days=hoy.weekday())  # Lunes de esta semana
            fecha_fin = fecha_inicio + timedelta(days=6)  # Domingo de esta semana
            fecha_inicio = make_aware(datetime.combine(fecha_inicio, datetime.min.time()))
            fecha_fin = make_aware(datetime.combine(fecha_fin, datetime.max.time()))

        # Filtrar el modelo Gasto por el rango de fechas
        if fecha_inicio and fecha_fin:
            context['gastos'] = Gasto.objects.filter(fecha__range=(fecha_inicio, fecha_fin)).order_by('-fecha')
        else:
            context['gastos'] = Gasto.objects.all().order_by('-fecha')

        # Añadir las fechas al contexto para el formulario
        context['fecha_inicio'] = fecha_inicio_str if fecha_inicio_str else fecha_inicio.strftime('%Y-%m-%d')
        context['fecha_fin'] = fecha_fin_str if fecha_fin_str else fecha_fin.strftime('%Y-%m-%d')

        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('accion') == 'eliminar':
            gasto_id = request.POST.get('gasto_id')
            if gasto_id:
                gasto = get_object_or_404(Gasto, id=gasto_id)
                gasto.delete()
                return JsonResponse({'success': True, 'message': 'Gasto eliminado correctamente.'})
        return super().get(request, *args, **kwargs)

class GastoCreateView(CreateView):
    model = Gasto
    template_name = 'asador/gastos/crear_gasto.html'
    form_class = GastoForm
    success_url = reverse_lazy('lista_gastos')

class GastoUpdateView(UpdateView):
    model = Gasto
    template_name = 'asador/gastos/editar_gasto.html'
    form_class = GastoForm
    success_url = reverse_lazy('lista_gastos')

    def get_initial(self):
        initial = super().get_initial()
        gasto = self.get_object()
        # Establecer la fecha en formato compatible con datetime-local
        initial['fecha'] = gasto.fecha.strftime('%Y-%m-%d')  # Convierte a YYYY-MM-DD
        return initial
