from datetime import datetime, timedelta
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils.timezone import make_aware
from django.views.generic.base import TemplateView
from django.http import JsonResponse
from base.models import GastosTienda, GastosPersonales, PagosBanco
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from base.forms import GastosTiendaForm, GastosPersonalesForm, PagosBancoForm

class GastosPagosListView(LoginRequiredMixin, TemplateView):
    template_name = 'carniceria/gastos_pagos/lista_gastos_pagos_tienda.html'

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

        # Filtrar ambas tablas por el rango de fechas si es válido
        if fecha_inicio and fecha_fin:
            context['gastos_tienda'] = GastosTienda.objects.filter(fecha__range=(fecha_inicio, fecha_fin)).order_by('-fecha')
            context['gastos_personales'] = GastosPersonales.objects.filter(fecha__range=(fecha_inicio, fecha_fin)).order_by('-fecha')
            context['pagos_banco'] = PagosBanco.objects.filter(fecha__range=(fecha_inicio, fecha_fin)).order_by('-fecha')
        else:
            context['gastos_tienda'] = GastosTienda.objects.all().order_by('-fecha')
            context['gastos_personales'] = GastosPersonales.objects.all().order_by('-fecha')
            context['pagos_banco'] = PagosBanco.objects.all().order_by('-fecha')

        # Añadir las fechas al contexto para el formulario
        context['fecha_inicio'] = fecha_inicio_str if fecha_inicio_str else fecha_inicio.strftime('%Y-%m-%d')
        context['fecha_fin'] = fecha_fin_str if fecha_fin_str else fecha_fin.strftime('%Y-%m-%d')

        return context

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            accion = data.get('accion')
            registro_id = data.get('registro_id')

            if accion == 'eliminar_gasto' and registro_id:
                gasto = get_object_or_404(GastosTienda, id=registro_id)
                gasto.delete()
                return JsonResponse({'success': True, 'message': 'Gasto eliminado correctamente.'})
            
            elif accion == 'eliminar_gasto_personal' and registro_id:
                gasto_personal = get_object_or_404(GastosPersonales, id=registro_id)
                gasto_personal.delete()
                return JsonResponse({'success': True, 'message': 'Gasto personal eliminado correctamente.'})

            elif accion == 'eliminar_pago' and registro_id:
                pago = get_object_or_404(PagosBanco, id=registro_id)
                pago.delete()
                return JsonResponse({'success': True, 'message': 'Pago eliminado correctamente.'})

            return JsonResponse({'success': False, 'message': 'Acción no válida o registro no encontrado.'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Error al procesar los datos JSON.'})

class GastosTiendaCreateView(CreateView):
    model = GastosTienda
    form_class = GastosTiendaForm
    template_name = 'carniceria/gastos_pagos/crear_gasto_tienda.html'
    success_url = reverse_lazy('lista_gastos_pagos_tienda')


class GastosTiendaUpdateView(UpdateView):
    model = GastosTienda
    form_class = GastosTiendaForm
    template_name = 'carniceria/gastos_pagos/editar_gasto_tienda.html'
    success_url = reverse_lazy('lista_gastos_pagos_tienda')

    def get_initial(self):
        initial = super().get_initial()
        gasto = self.get_object()
        initial['fecha'] = gasto.fecha.strftime('%Y-%m-%d')  # Formato YYYY-MM-DD
        return initial

class GastosPersonalesCreateView(CreateView):
    model = GastosPersonales
    form_class = GastosPersonalesForm
    template_name = 'carniceria/gastos_pagos/crear_gasto_personal.html'
    success_url = reverse_lazy('lista_gastos_pagos_tienda')


class GastosPersonalesUpdateView(UpdateView):
    model = GastosPersonales
    form_class = GastosPersonalesForm
    template_name = 'carniceria/gastos_pagos/editar_gasto_personal.html'
    success_url = reverse_lazy('lista_gastos_pagos_tienda')

    def get_initial(self):
        initial = super().get_initial()
        gasto = self.get_object()
        initial['fecha'] = gasto.fecha.strftime('%Y-%m-%d')  # Formato YYYY-MM-DD
        return initial
    
class PagosBancoCreateView(CreateView):
    model = PagosBanco
    form_class = PagosBancoForm
    template_name = 'carniceria/gastos_pagos/crear_pago_banco.html'
    success_url = reverse_lazy('lista_gastos_pagos_tienda')


class PagosBancoUpdateView(UpdateView):
    model = PagosBanco
    form_class = PagosBancoForm
    template_name = 'carniceria/gastos_pagos/editar_pago_banco.html'
    success_url = reverse_lazy('lista_gastos_pagos_tienda')

    def get_initial(self):
        initial = super().get_initial()
        pago = self.get_object()
        initial['fecha'] = pago.fecha.strftime('%Y-%m-%d')  # Formato YYYY-MM-DD
        return initial