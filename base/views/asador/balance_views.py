import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from base.models import Gasto, ResumenVentas
from django.db.models import Sum
from decimal import Decimal

class BalanceAsadorView(LoginRequiredMixin, View):
    # Configuración de LoginRequiredMixin
    login_url = 'login'
    redirect_field_name = None

    def get(self, request):
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        # Filtrar las ventas según las fechas seleccionadas
        if fecha_inicio and fecha_fin:
            resumen_ventas = ResumenVentas.objects.filter(fecha__range=[fecha_inicio, fecha_fin]).order_by('fecha')
            gastos = Gasto.objects.filter(fecha__range=[fecha_inicio, fecha_fin]).order_by('fecha')
        else:
            resumen_ventas = ResumenVentas.objects.all().order_by('fecha')
            gastos = Gasto.objects.all().order_by('fecha')

        # Convertir los QuerySets a listas de diccionarios y formatear fechas
        resumen_ventas_list = list(resumen_ventas.values())
        for item in resumen_ventas_list:
            item['fecha'] = item['fecha'].strftime('%Y-%m-%d')  # Convertir a cadena
            item['total_ventas'] = float(item['total_ventas'])  # Convertir a float
            item['total_pollos'] = float(item['total_pollos'])  # Convertir a float
            item['total_cachopos'] = float(item['total_cachopos'])  # Convertir a float

        gastos_list = list(gastos.values())
        for item in gastos_list:
            item['fecha'] = item['fecha'].strftime('%Y-%m-%d')  # Convertir a cadena
            item['monto'] = float(item['monto'])  # Convertir a float

        # Calcular totales
        total_ventas = resumen_ventas.aggregate(Sum('total_ventas'))['total_ventas__sum'] or Decimal('0.00')
        numero_pedidos = resumen_ventas.aggregate(Sum('numero_pedidos'))['numero_pedidos__sum'] or 0
        total_pollos = resumen_ventas.aggregate(Sum('total_pollos'))['total_pollos__sum'] or Decimal('0.00')
        total_cachopos = resumen_ventas.aggregate(Sum('total_cachopos'))['total_cachopos__sum'] or 0

        # Obtener total de los gastos
        total_gastos = gastos.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')

        # Calcular beneficios
        total_beneficios = total_ventas - total_gastos

        context = {
            'resumen_ventas': json.dumps(resumen_ventas_list),  # Lista de registros detallados de ventas
            'gastos': json.dumps(gastos_list),  # Lista de registros detallados de gastos
            'total_ventas': total_ventas,
            'total_gastos': total_gastos,
            'total_beneficios': total_beneficios,
            'numero_pedidos': numero_pedidos,
            'total_pollos': total_pollos,
            'total_cachopos': total_cachopos,
        }
        return render(request, 'asador/balance/balance.html', context)
