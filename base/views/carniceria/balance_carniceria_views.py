import json
from django.shortcuts import render
from django.views import View
from django.db.models import Sum, Q
from decimal import Decimal
from base.models import Venta, FacturasIVA, FacturaTienda, GastosTienda, GastosPersonales, PagosBanco

class BalanceCarniceriaView(View):
    def get(self, request):
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        # Filtrar registros según las fechas seleccionadas
        filtros = Q()
        if fecha_inicio and fecha_fin:
            filtros &= Q(fecha__range=[fecha_inicio, fecha_fin])

        # Obtener y sumar el total de ventas
        total_ventas = Venta.objects.filter(filtros).aggregate(total=Sum('total'))['total'] or Decimal('0.00')

        # Obtener y sumar los totales de compras
        total_facturas_iva = FacturasIVA.objects.filter(filtros).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        total_facturas_tienda = FacturaTienda.objects.filter(filtros).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        compras = total_facturas_iva + total_facturas_tienda

        # Obtener y sumar los totales de gastos
        total_gastos_tienda = GastosTienda.objects.filter(filtros).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        total_pagos_banco = PagosBanco.objects.filter(filtros).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
        gastos = total_gastos_tienda + total_pagos_banco

        # Calcular beneficios
        beneficios = total_ventas - compras - gastos

        context = {
            'ventas': total_ventas,
            'compras': compras,
            'gastos': gastos,
            'beneficios': beneficios,
        }
        return render(request, 'carniceria/balance/balance.html', context)
