from django import forms
from .models import Pedido, PedidoProducto, PedidoMenu, Menu, MenuProducto, Gasto, Venta, FacturasIVA, FacturaTienda, Capital, GastosTienda, GastosPersonales, PagosBanco, Cliente, Factura, FacturaProducto
from django.forms import DateTimeInput, inlineformset_factory
from django.utils import timezone
from django.forms import formset_factory

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['nombre_cliente', 'fecha_hora', 'observaciones']
        widgets = {
            'fecha_hora': DateTimeInput(attrs={
                'type': 'datetime-local',  # Esto permite un selector de fecha y hora
                'class': 'form-control'  # Puedes agregar clases CSS para el estilo
            })
        }

class PedidoProductoForm(forms.ModelForm):
    class Meta:
        model = PedidoProducto
        fields = ['producto', 'cantidad']

class PedidoMenuForm(forms.ModelForm):
    class Meta:
        model = PedidoMenu
        fields = ['menu', 'cantidad']


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['nombre', 'precio']

class MenuProductoForm(forms.ModelForm):
    class Meta:
        model = MenuProducto
        fields = ['producto', 'cantidad']

class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = [ 'fecha', 'descripcion', 'monto']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',  # Esto permite un selector de fecha
                'class': 'form-control'  # Clases CSS para el estilo
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control'  # Clases CSS para el estilo
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control'  # Clases CSS para el estilo
            }),
        }

class FacturasIVAForm(forms.ModelForm):
    class Meta:
        model = FacturasIVA
        fields = ['fecha', 'proveedor', 'numero_factura', 'total', 'pagada']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',  # Esto permite un selector de fecha
                'class': 'form-control'  # Clases CSS para el estilo
            }),
            'total': forms.NumberInput(attrs={
                'class': 'form-control'  # Clases CSS para el estilo
            }),
            'numero_factura': forms.TextInput(attrs={
                'class': 'form-control'  # Clases CSS para el estilo
            }),
            'proveedor': forms.TextInput(attrs={
                'class': 'form-control'  # Clases CSS para el estilo
            }),
        }

class FacturaTiendaForm(forms.ModelForm):
    class Meta:
        model = FacturaTienda
        fields = ['fecha', 'proveedor', 'total', 'pagada']
        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',  # Esto permite un selector de fecha
                'class': 'form-control'  # Clases CSS para el estilo
            }),
            'total': forms.NumberInput(attrs={
                'class': 'form-control'  # Clases CSS para el estilo
            }),
            'proveedor': forms.TextInput(attrs={
                'class': 'form-control'  # Clases CSS para el estilo
            }),
        }

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['fecha', 'total']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'total': forms.NumberInput(attrs={'step': '0.01'}),
        }
        labels = {
            'fecha': 'Fecha de la venta',
            'total': 'Total (€)',
        }

class CapitalForm(forms.ModelForm):
    class Meta:
        model = Capital
        fields = ['fecha', 'tipo_ingreso', 'total']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_ingreso': forms.Select(attrs={'class': 'form-control'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total del capital'}),
        }
        labels = {
            'fecha': 'Fecha',
            'tipo_ingreso': 'Tipo de Ingreso',
            'total': 'Total (€)',
        }

class GastosTiendaForm(forms.ModelForm):
    class Meta:
        model = GastosTienda
        fields = ['fecha', 'gasto', 'total']  # Campos del modelo
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gasto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción del gasto'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total (€)'}),
        }
        labels = {
            'fecha': 'Fecha',
            'gasto': 'Descripción del Gasto',
            'total': 'Total (€)',
        }

class GastosPersonalesForm(forms.ModelForm):
    class Meta:
        model = GastosPersonales  # Reemplaza con el nombre correcto del modelo si es diferente
        fields = ['fecha', 'gasto', 'total']  # Campos del modelo
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gasto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción del gasto'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total (€)'}),
        }
        labels = {
            'fecha': 'Fecha',
            'gasto': 'Descripción del Gasto',
            'total': 'Total (€)',
        }


class PagosBancoForm(forms.ModelForm):
    class Meta:
        model = PagosBanco
        fields = ['fecha', 'concepto', 'total']  # Campos del modelo
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'concepto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Concepto del pago'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total (€)'}),
        }
        labels = {
            'fecha': 'Fecha',
            'concepto': 'Concepto',
            'total': 'Total (€)',
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'codigo', 'direccion', 'cif_dni']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código único'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Dirección completa', 'rows': 3}),
            'cif_dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CIF o DNI'}),
        }
        labels = {
            'nombre': 'Nombre',
            'codigo': 'Código',
            'direccion': 'Dirección',
            'cif_dni': 'CIF/DNI',
        }

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['cliente', 'numero_factura']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'numero_factura': forms.TextInput(attrs={'class': 'form-control'}),
        }

class FacturaProductoForm(forms.ModelForm):
    class Meta:
        model = FacturaProducto
        fields = ['descripcion', 'cantidad', 'precio_kg']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción del producto'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad en kg'}),
            'precio_kg': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio por kg (€)'}),
        }

FacturaProductoFormSet = inlineformset_factory( 
    Factura, FacturaProducto, form=FacturaProductoForm, extra=0, can_delete=True
)