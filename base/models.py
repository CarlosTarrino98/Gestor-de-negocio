from django.utils import timezone
from decimal import Decimal
from django.db import models


# Creación de modelos que son las tablas de la base de datos

################ ASADOR ################
class Producto(models.Model):
    # Categorías de productos disponibles
    CATEGORIAS = [
        ('principal', 'Principal'),
        ('raciones', 'Raciones'),
        ('bebida', 'Bebida'),
        ('postre', 'Postre'),
    ]

    nombre = models.CharField(max_length=100)  # Nombre del producto
    categoria = models.CharField(max_length=10, choices=CATEGORIAS)  # Categoría del producto
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Precio del producto

    def __str__(self):
        return f"{self.nombre} ({self.categoria})"


class Menu(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre del menú
    productos = models.ManyToManyField(Producto, through='MenuProducto')  # Relación ManyToMany usando MenuProducto
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Precio total del menú

    def __str__(self):
        return self.nombre

class MenuProducto(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)  # Relación con el menú
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # Relación con el producto
    cantidad = models.PositiveIntegerField(default=1)  # Cantidad de producto en el menú

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en el menú {self.menu.nombre}"

class Pedido(models.Model):
    nombre_cliente = models.CharField(max_length=100)  # Nombre del cliente que realiza el pedido
    fecha_hora = models.DateTimeField()  # Fecha y hora en que se entregará el pedido
    entregado = models.BooleanField(default=False)  # Campo para indicar si el pedido ha sido entregado
    observaciones = models.TextField(blank=True, null=True)  # Campo para observaciones opcionales
    
    def __str__(self):
        return f"Pedido de {self.nombre_cliente}"

    class Meta:
        ordering = ['fecha_hora']  # Ordenar por fecha_hora


class PedidoProducto(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)  # Relación con el pedido
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # Relación con el producto
    cantidad = models.PositiveIntegerField(default=1)  # Cantidad del producto en el pedido

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en el pedido de {self.pedido.nombre_cliente}"


class PedidoMenu(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)  # Relación con el pedido
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)  # Relación con el menú
    cantidad = models.PositiveIntegerField(default=1)  # Cantidad de menús en el pedido

    def __str__(self):
        return f"{self.cantidad} x {self.menu.nombre} en el pedido de {self.pedido.nombre_cliente}"


class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE)  # Relación uno a uno con Producto
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Cantidad de producto disponible en inventario

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad_disponible} unidades"


class Gasto(models.Model):
    descripcion = models.CharField(max_length=255)  # Descripción del gasto
    monto = models.DecimalField(max_digits=10, decimal_places=2)  # Monto del gasto
    fecha = models.DateField()  # Fecha del gasto

    def __str__(self):
        return f"{self.descripcion} - {self.monto}€"


class ResumenVentas(models.Model):
    fecha = models.DateField(auto_now_add=True)  # Fecha de la venta (se asigna automáticamente la fecha actual)
    total_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Monto total de ventas en euros
    numero_pedidos = models.PositiveIntegerField(default=0)  # Número total de pedidos realizados en el día
    total_pollos = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Total de pollos vendidos
    total_cachopos = models.PositiveIntegerField(default=0)  # Total de cachopos vendidos

    def __str__(self):
        return (f"Resumen del {self.fecha}: {self.total_ventas}€ en {self.numero_pedidos} pedidos, "
                f"{self.total_pollos} pollos, {self.total_cachopos} cachopos")

    class Meta:
        ordering = ['-fecha']  # Ordenar por fecha descendente, mostrando el resumen más reciente primero


################ CARNICERIA ################
class Venta(models.Model):
    fecha = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.fecha} - {self.total}€"

class FacturasIVA(models.Model):
    proveedor = models.CharField(max_length=100)  # Nombre del proveedor
    numero_factura = models.CharField(max_length=50)  # Número de la factura
    fecha = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Total de la factura
    pagada = models.BooleanField(default=False)  # Indicador si la factura está pagada

    def __str__(self):
        estado = "Pagada" if self.pagada else "Pendiente"
        return f"Factura {self.numero_factura} de {self.proveedor} - {self.total}€ ({estado})"

    class Meta:
        ordering = ['-fecha']  # Ordenar las facturas de forma descendente por fecha

class FacturaTienda(models.Model):
    proveedor = models.CharField(max_length=100)  # Nombre del proveedor
    fecha = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Total de la factura
    pagada = models.BooleanField(default=False)  # Indicador si la factura está pagada

    def __str__(self):
        return f"Factura de {self.proveedor} - {self.total}€"
    
    class Meta:
        ordering = ['-fecha']  # Ordenar las facturas de forma descendente por fecha

class GastosTienda(models.Model):
    fecha = models.DateField(verbose_name="Fecha")
    gasto = models.CharField(max_length=255, verbose_name="Descripción del gasto")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total")

    def __str__(self):
        return f"{self.fecha} - {self.gasto} - {self.total} €"

class GastosPersonales(models.Model):
    fecha = models.DateField(verbose_name="Fecha")
    gasto = models.CharField(max_length=255, verbose_name="Descripción del gasto")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total")

    def __str__(self):
        return f"{self.fecha} - {self.gasto} - {self.total} €"

class PagosBanco(models.Model):
    fecha = models.DateField(verbose_name="Fecha")
    concepto = models.CharField(max_length=255, verbose_name="Concepto")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total")

    def __str__(self):
        return f"{self.fecha} - {self.concepto} - {self.total} €"
    
class Capital(models.Model):
    TIPOS_INGRESO = [
        ('EF', 'Efectivo'),
        ('BB', 'BBVA'),
        ('S1', 'Santander 1'),
        ('S2', 'Santander 2'),
        ('HI', 'Hida'),
        ('ES', 'Esmeralda'),
        ('FA', 'Factory'),
        ('VA', 'Varios'),
        ('TA', 'Tarjetas'),
    ]

    fecha = models.DateField(verbose_name="Fecha")
    tipo_ingreso = models.CharField(max_length=2, choices=TIPOS_INGRESO, verbose_name="Tipo de ingreso")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total")

    def __str__(self):
        return f"{self.get_tipo_ingreso_display()} - {self.fecha} - {self.total}€"

class Cliente(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    direccion = models.TextField(verbose_name="Dirección")
    cif_dni = models.CharField(max_length=50, unique=True, verbose_name="CIF/DNI")

    def __str__(self):
        return f"{self.codigo}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'codigo': self.codigo,
            'direccion': self.direccion,
            'cif_dni': self.cif_dni,
        }

class Factura(models.Model):
    nombre_empresa = models.CharField(max_length=100, default="PETTISSO", editable=False)
    telefono_empresa = models.CharField(max_length=20, default="123456789", editable=False)
    email_empresa = models.EmailField(default="ejemplo@hotmail.com", editable=False)
    numero_factura = models.CharField(max_length=20)
    fecha_emision = models.DateField(default=timezone.now, editable=False)
    fecha_entrega = models.DateField(default=timezone.now, editable=False)
    nombre_emisor = models.CharField(max_length=100, default="Alfredo Martínez Simón", editable=False)
    direccion_emisor = models.CharField(max_length=255, default="Avda. Ejemplo, Alcalá de Henares, España", editable=False)
    cif_nif_emisor = models.CharField(max_length=20, default="98765432B", editable=False)
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    total_neto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        # Solo calcular los totales si la instancia ya tiene una clave primaria
        if self.pk:
            self.total_neto = sum(producto.total_neto for producto in self.facturaproducto_set.all())
            self.total_iva = sum(producto.iva for producto in self.facturaproducto_set.all())
            self.total = sum(producto.total for producto in self.facturaproducto_set.all())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Factura {self.numero_factura} - {self.cliente.nombre}"

class FacturaProducto(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)
    precio_kg = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    total_neto = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    def save(self, *args, **kwargs):
        # Calcular el total neto (sin IVA) y el IVA
        self.total_neto = self.cantidad * self.precio_kg
        self.iva = self.total_neto * Decimal('0.10')
        # Calcular el total (con IVA)
        self.total = self.total_neto + self.iva
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} kg de {self.descripcion} a {self.precio_kg} €/kg en la factura {self.factura.numero_factura}"

