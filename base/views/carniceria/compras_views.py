from datetime import datetime, timedelta
import json
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.http import JsonResponse
from base.forms import FacturaTiendaForm, FacturasIVAForm
from base.models import FacturasIVA, FacturaTienda
from django.views.generic.base import TemplateView
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta

class CompraListView(TemplateView):
    template_name = 'carniceria/compras/lista_compras.html'

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
            # Calcular el lunes de la semana en curso (inicio de la semana)
            fecha_inicio = hoy - timedelta(days=hoy.weekday())  # Lunes de esta semana
            # Calcular el domingo de la semana en curso (fin de la semana)
            fecha_fin = fecha_inicio + timedelta(days=6)  # Domingo de esta semana
            # Convertir a datetime y hacer aware
            fecha_inicio = make_aware(datetime.combine(fecha_inicio, datetime.min.time()))
            fecha_fin = make_aware(datetime.combine(fecha_fin, datetime.max.time()))

        # Filtrar ambas tablas por el rango de fechas si es válido
        if fecha_inicio and fecha_fin:
            context['facturas_iva'] = FacturasIVA.objects.filter(fecha__range=(fecha_inicio, fecha_fin)).order_by('-fecha')
            context['facturas_tienda'] = FacturaTienda.objects.filter(fecha__range=(fecha_inicio, fecha_fin)).order_by('-fecha')
        else:
            context['facturas_iva'] = FacturasIVA.objects.all().order_by('-fecha')
            context['facturas_tienda'] = FacturaTienda.objects.all().order_by('-fecha')

        # Añadir las fechas al contexto para el formulario
        context['fecha_inicio'] = fecha_inicio_str if fecha_inicio_str else fecha_inicio.strftime('%Y-%m-%d')
        context['fecha_fin'] = fecha_fin_str if fecha_fin_str else fecha_fin.strftime('%Y-%m-%d')

        return context

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            accion = data.get('accion')
            factura_id = data.get('factura_id')
            print(accion, factura_id)  # Depurar valores

            if accion == 'eliminar_factura_iva' and factura_id:
                factura = get_object_or_404(FacturasIVA, id=factura_id)
                factura.delete()
                return JsonResponse({'success': True, 'message': 'Factura IVA eliminada correctamente.'})

            elif accion == 'eliminar_factura_tienda' and factura_id:
                factura = get_object_or_404(FacturaTienda, id=factura_id)
                factura.delete()
                return JsonResponse({'success': True, 'message': 'Factura Tienda eliminada correctamente.'})

            elif accion == 'marcar_pagada' and factura_id:
                factura = get_object_or_404(FacturasIVA, id=factura_id)
                factura.pagada = True
                factura.save()
                return JsonResponse({'success': True, 'message': 'Factura marcada como pagada.'})

            elif accion == 'desmarcar_pagada' and factura_id:
                factura = get_object_or_404(FacturasIVA, id=factura_id)
                factura.pagada = False
                factura.save()
                return JsonResponse({'success': True, 'message': 'Factura desmarcada como pagada.'})
            
            elif accion == 'marcar_pagada_tienda' and factura_id:
                factura = get_object_or_404(FacturaTienda, id=factura_id)
                factura.pagada = True
                factura.save()
                return JsonResponse({'success': True, 'message': 'Factura marcada como pagada.'})

            elif accion == 'desmarcar_pagada_tienda' and factura_id:
                factura = get_object_or_404(FacturaTienda, id=factura_id)
                factura.pagada = False
                factura.save()
                return JsonResponse({'success': True, 'message': 'Factura desmarcada como pagada.'})

            return JsonResponse({'success': False, 'message': 'Acción no válida o factura no encontrada.'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Error al procesar los datos JSON.'})


class CompraIvaCreateView(CreateView):
    model = FacturasIVA
    form_class = FacturasIVAForm
    template_name = 'carniceria/compras/crear_compra_iva.html'
    success_url = reverse_lazy('lista_compras')


class CompraIvaUpdateView(UpdateView):
    model = FacturasIVA
    form_class = FacturasIVAForm
    template_name = 'carniceria/compras/editar_compra_iva.html'
    success_url = reverse_lazy('lista_compras')

    def get_initial(self):
        initial = super().get_initial()
        facturasIVA = self.get_object()
        # Establecer la fecha en formato compatible con datetime-local
        initial['fecha'] = facturasIVA.fecha.strftime('%Y-%m-%d')  # Convierte a YYYY-MM-DD
        return initial

class CompraTiendaCreateView(CreateView):
    model = FacturaTienda
    form_class = FacturaTiendaForm
    template_name = 'carniceria/compras/crear_compra_tienda.html'
    success_url = reverse_lazy('lista_compras')


class CompraTiendaUpdateView(UpdateView):
    model = FacturaTienda
    form_class = FacturaTiendaForm
    template_name = 'carniceria/compras/editar_compra_tienda.html'
    success_url = reverse_lazy('lista_compras')

    def get_initial(self):
        initial = super().get_initial()
        facturasTienda = self.get_object()
        # Establecer la fecha en formato compatible con datetime-local
        initial['fecha'] = facturasTienda.fecha.strftime('%Y-%m-%d')  # Convierte a YYYY-MM-DD
        return initial
