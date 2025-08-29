from django.contrib import admin
from .models import Producto, Menu, MenuProducto, Pedido, PedidoProducto, PedidoMenu, Inventario, Gasto, FacturasIVA, FacturaTienda, Venta, Capital, GastosTienda, PagosBanco, Cliente

# Inline para productos en el pedido
class PedidoProductoInline(admin.TabularInline):
    model = PedidoProducto
    extra = 1  # Número de formularios vacíos que se mostrarán

# Inline para menús en el pedido
class PedidoMenuInline(admin.TabularInline):
    model = PedidoMenu
    extra = 1  # Número de formularios vacíos que se mostrarán

# Inline para productos en el menú
class MenuProductoInline(admin.TabularInline):
    model = MenuProducto
    extra = 1  # Número de formularios vacíos que se mostrarán

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    inlines = [PedidoProductoInline, PedidoMenuInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Si estamos en la vista de agregar, no mostrar inlines aún
        if request.resolver_match.url_name == 'admin:base_pedido_add':
            pass
        return qs

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    inlines = [MenuProductoInline]

@admin.register(Capital)
class CapitalAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo_ingreso', 'total')
    list_filter = ('tipo_ingreso',)

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'total')
    search_fields = ('fecha',)
    list_filter = ('fecha',)

@admin.register(GastosTienda)
class GastosTiendaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'gasto', 'total')
    list_filter = ('fecha',)

@admin.register(PagosBanco)
class PagosBancoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'concepto', 'total')
    list_filter = ('fecha',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'direccion', 'cif_dni')
    search_fields = ('nombre', 'codigo', 'cif_dni')
    list_filter = ('codigo',)

# Registra los otros modelos
admin.site.register(Producto)
admin.site.register(Inventario)
admin.site.register(Gasto)
admin.site.register(FacturasIVA)
admin.site.register(FacturaTienda)


