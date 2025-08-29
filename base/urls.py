from django.urls import path
from .views.home_views import home
from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib.auth import views as auth_views
from django.urls import path

# Importa las vistas de los archivos correspondientes
from .views.asador.pedidos_views import (
    PedidoListView,
    PedidoCreateView,
    PedidoUpdateView,
)

from .views.asador.productos_views import (
    ProductoListView,
    ProductoCreateView,
    ProductoUpdateView,
)

from .views.asador.menus_views import (
    MenuListView,
    MenuCreateView,
    MenuUpdateView,
)

from .views.asador.inventario_views import (
    InventarioListView,
    InventarioCreateView,
    InventarioUpdateView,
)

from .views.asador.gastos_views import (
    GastoListView,
    GastoCreateView,
    GastoUpdateView,
)

from .views.asador.balance_views import (
    BalanceAsadorView,
)

from .views.carniceria.ventas_views import (
    VentaListView,
    VentaCreateView,
    VentaUpdateView,
)

from .views.carniceria.compras_views import (
    CompraListView,
    CompraIvaCreateView,
    CompraIvaUpdateView,
    CompraTiendaCreateView,
    CompraTiendaUpdateView
)

from .views.carniceria.gastos_pagos_tienda_views import (
    GastosPagosListView,
    GastosTiendaCreateView,
    GastosTiendaUpdateView,
    GastosPersonalesCreateView,
    GastosPersonalesUpdateView,
    PagosBancoCreateView,
    PagosBancoUpdateView,
)

from .views.carniceria.capital_views import (
    CapitalListView,
    CapitalCreateView,
    CapitalUpdateView,
)

from .views.carniceria.clientes_views import (
    ClienteListView,
    ClienteCreateView,
    ClienteUpdateView,
)

from .views.carniceria.facturas_views import (
    FacturaListView,
    FacturaCreateView,
    FacturaUpdateView,
    FacturaPreviewView,
)

from .views.carniceria.balance_carniceria_views import (
    BalanceCarniceriaView,
)

urlpatterns = [
    # Ruta para el login
    path('login/', auth_views.LoginView.as_view(template_name='login/login.html'), name='login'),

    # Ruta principal
    path('', home, name='home'),

    ## RUTAS ASADOR ##
    # Rutas para Pedidos
    path('pedidos/', PedidoListView.as_view(), name='lista_pedidos'),
    path('pedidos/nuevo/', PedidoCreateView.as_view(), name='crear_pedido'),
    path('pedidos/<int:pk>/editar/', PedidoUpdateView.as_view(), name='editar_pedido'),

    # Rutas para Productos
    path('productos/', ProductoListView.as_view(), name='lista_productos'),
    path('productos/nuevo/', ProductoCreateView.as_view(), name='crear_producto'),
    path('productos/<int:pk>/editar/', ProductoUpdateView.as_view(), name='editar_producto'),

    # Rutas para Menús
    path('menus/', MenuListView.as_view(), name='lista_menus'),
    path('menus/nuevo/', MenuCreateView.as_view(), name='crear_menu'),
    path('menus/<int:pk>/editar/', MenuUpdateView.as_view(), name='editar_menu'),

    # Rutas para Inventario
    path('inventario/', InventarioListView.as_view(), name='lista_inventario'),
    path('inventario/crear/', InventarioCreateView.as_view(), name='crear_inventario'),
    path('inventario/editar/<int:pk>/', InventarioUpdateView.as_view(), name='editar_inventario'),

    # Rutas para Gastos
    path('gastos/', GastoListView.as_view(), name='lista_gastos'),
    path('gastos/nuevo/', GastoCreateView.as_view(), name='crear_gasto'),
    path('gastos/<int:pk>/editar/', GastoUpdateView.as_view(), name='editar_gasto'),

    # Ruta para Balance
    path('balance/asador/', BalanceAsadorView.as_view(), name='balance_asador'),

    ## RUTAS CARNICERIA ##
    # Rutas para Ventas
    path('ventas/', VentaListView.as_view(), name='lista_ventas'),
    path('ventas/nueva/', VentaCreateView.as_view(), name='crear_venta'),
    path('ventas/<int:pk>/editar/', VentaUpdateView.as_view(), name='editar_venta'),

    # Rutas para Compras
    path('compras/', CompraListView.as_view(), name='lista_compras'),
    path('compras/iva/nuevo/', CompraIvaCreateView.as_view(), name='crear_compra_iva'),
    path('compras/iva/<int:pk>/editar/', CompraIvaUpdateView.as_view(), name='editar_compra_iva'),
    path('compras/tienda/nuevo/', CompraTiendaCreateView.as_view(), name='crear_compra_tienda'),
    path('compras/tienda/<int:pk>/editar/', CompraTiendaUpdateView.as_view(), name='editar_compra_tienda'),

    # Rutas para GastosTienda
    path('gastos_tienda/', GastosPagosListView.as_view(), name='lista_gastos_pagos_tienda'),
    path('gastos_tienda/nuevo/', GastosTiendaCreateView.as_view(), name='crear_gasto_tienda'),
    path('gastos_tienda/<int:pk>/editar/', GastosTiendaUpdateView.as_view(), name='editar_gasto_tienda'),
    path('gastos_personales/nuevo/', GastosPersonalesCreateView.as_view(), name='crear_gasto_personal'),
    path('gastos_personales/<int:pk>/editar/', GastosPersonalesUpdateView.as_view(), name='editar_gasto_personal'),
    path('pagos_banco/nuevo/', PagosBancoCreateView.as_view(), name='crear_pago_banco'),
    path('pagos_banco/<int:pk>/editar/', PagosBancoUpdateView.as_view(), name='editar_pago_banco'),

    # Rutas para Capital
    path('capital/', CapitalListView.as_view(), name='lista_capital'),
    path('capital/nuevo/', CapitalCreateView.as_view(), name='crear_capital'),
    path('capital/<int:pk>/editar/', CapitalUpdateView.as_view(), name='editar_capital'),

    # Rutas para clientes
    path('clientes/', ClienteListView.as_view(), name='lista_clientes'),
    path('clientes/nuevo/', ClienteCreateView.as_view(), name='crear_cliente'),
    path('clientes/<int:pk>/editar/', ClienteUpdateView.as_view(), name='editar_cliente'),

    # Ruta para facturas
    path('facturas/', FacturaListView.as_view(), name='lista_facturas'),
    path('factura/nuevo/', FacturaCreateView.as_view(), name='crear_factura'),
    path('factura/<int:pk>/editar/', FacturaUpdateView.as_view(), name='editar_factura'),
    path('factura/<int:pk>/previsualizar/', FacturaPreviewView.as_view(), name='previsualizar_factura'),

    # Ruta para balance carniceria
    path('balance/carniceria/', BalanceCarniceriaView.as_view(), name='balance_carniceria'),

] + debug_toolbar_urls()
