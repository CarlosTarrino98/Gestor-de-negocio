from datetime import datetime, timedelta
import json
from django.shortcuts import get_object_or_404
from django.utils.timezone import make_aware
from django.views.generic.base import TemplateView
from django.http import JsonResponse
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from base.models import Venta
from base.forms import VentaForm


class VentaListView(TemplateView):
    template_name = 'carniceria/ventas/lista_ventas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener fechas de los parámetros GET
        fecha_inicio_str = self.request.GET.get('fecha_inicio')
        fecha_fin_str = self.request.GET.get('fecha_fin')

        if fecha_inicio_str and fecha_fin_str:
            try:
                fecha_inicio = make_aware(datetime.strptime(fecha_inicio_str, '%Y-%m-%d'))
                fecha_fin = make_aware(datetime.strptime(fecha_fin_str, '%Y-%m-%d')) + timedelta(days=1) - timedelta(seconds=1)
            except ValueError:
                fecha_inicio, fecha_fin = None, None
        else:
            hoy = datetime.now().date()
            fecha_inicio = hoy - timedelta(days=hoy.weekday())  
            fecha_fin = fecha_inicio + timedelta(days=6)
            fecha_inicio = make_aware(datetime.combine(fecha_inicio, datetime.min.time()))
            fecha_fin = make_aware(datetime.combine(fecha_fin, datetime.max.time()))

        # Filtrar ventas por rango de fechas
        if fecha_inicio and fecha_fin:
            context['ventas'] = Venta.objects.filter(fecha__range=(fecha_inicio, fecha_fin)).order_by('-fecha')
        else:
            context['ventas'] = Venta.objects.all().order_by('-fecha')

        context['fecha_inicio'] = fecha_inicio_str if fecha_inicio_str else fecha_inicio.strftime('%Y-%m-%d')
        context['fecha_fin'] = fecha_fin_str if fecha_fin_str else fecha_fin.strftime('%Y-%m-%d')

        return context

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            accion = data.get('accion')
            registro_id = data.get('registro_id')

            if accion == 'eliminar_venta' and registro_id:
                venta = get_object_or_404(Venta, id=registro_id)
                venta.delete()
                return JsonResponse({'success': True, 'message': 'Venta eliminada correctamente.'})

            return JsonResponse({'success': False, 'message': 'Acción no válida o registro no encontrado.'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Error al procesar los datos JSON.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error inesperado: {str(e)}'})


class VentaCreateView(CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'carniceria/ventas/crear_venta.html'
    success_url = reverse_lazy('lista_ventas')


class VentaUpdateView(UpdateView):
    model = Venta
    form_class = VentaForm
    template_name = 'carniceria/ventas/editar_venta.html'
    success_url = reverse_lazy('lista_ventas')

    def get_initial(self):
        initial = super().get_initial()
        venta = self.get_object()
        initial['fecha'] = venta.fecha.strftime('%Y-%m-%d')
        return initial
