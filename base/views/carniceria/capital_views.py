from datetime import datetime, timedelta
import json
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView
from django.http import JsonResponse
from django.utils.timezone import make_aware
from base.forms import CapitalForm
from base.models import Capital
from django.db.models import Sum


class CapitalListView(TemplateView):
    template_name = 'carniceria/capital/lista_capital.html'

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

        # Filtrar las ventas por el rango de fechas y excluir las de tipo 'TA' (Tarjetas)
        if fecha_inicio and fecha_fin:
            capitales = Capital.objects.filter(fecha__range=(fecha_inicio, fecha_fin)).exclude(tipo_ingreso='TA').order_by('-fecha')
        else:
            capitales = Capital.objects.exclude(tipo_ingreso='TA').order_by('-fecha')

        # Calcular el total de capitales excluyendo el tipo 'TA' (Tarjetas)
        total_capitales = Capital.objects.filter(fecha__range=(fecha_inicio, fecha_fin)).exclude(tipo_ingreso='TA').aggregate(total=Sum('total'))['total'] or 0

        # obtener el objeto de capitales
        tarjetas = Capital.objects.filter(tipo_ingreso='TA', fecha__range=(fecha_inicio, fecha_fin))
        
        # Calcular el total de capitales con tipo 'TA' (Tarjetas)
        total_tarjetas = tarjetas.aggregate(total=Sum('total'))['total'] or 0

        # Añadir las capitales y los totales al contexto
        context['capitales'] = capitales
        context['total_capitales'] = total_capitales
        context['tarjetas'] = tarjetas
        context['total_tarjetas'] = total_tarjetas

        # Añadir las fechas al contexto para el formulario
        context['fecha_inicio'] = fecha_inicio_str if fecha_inicio_str else fecha_inicio.strftime('%Y-%m-%d')
        context['fecha_fin'] = fecha_fin_str if fecha_fin_str else fecha_fin.strftime('%Y-%m-%d')

        return context

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            accion = data.get('accion')
            capital_id = data.get('capital_id')

            if accion == 'eliminar_capital' and capital_id:
                capital = get_object_or_404(Capital, id=capital_id)
                capital.delete()
                return JsonResponse({'success': True, 'message': 'Capital eliminado correctamente.'})

            return JsonResponse({'success': False, 'message': 'Acción no válida o capital no encontrado.'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Error al procesar los datos JSON.'})


class CapitalCreateView(CreateView):
    model = Capital
    form_class = CapitalForm
    template_name = 'carniceria/capital/crear_capital.html'
    success_url = reverse_lazy('lista_capital')


class CapitalUpdateView(UpdateView):
    model = Capital
    form_class = CapitalForm
    template_name = 'carniceria/capital/editar_capital.html'
    success_url = reverse_lazy('lista_capital')

    def get_initial(self):
        initial = super().get_initial()
        capital = self.get_object()
        # Establecer la fecha en formato compatible con datetime-local
        initial['fecha'] = capital.fecha.strftime('%Y-%m-%d')  # Convierte a YYYY-MM-DD
        return initial
