from datetime import datetime, timedelta
from decimal import Decimal
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.http import JsonResponse
from base.forms import PedidoForm
from base.models import Inventario, Menu, Pedido, PedidoMenu, PedidoProducto, Producto, ResumenVentas

# Listar todos los pedidos
class PedidoListView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'asador/pedidos/lista_pedidos.html'
    context_object_name = 'pedidos'

    # Configuración de LoginRequiredMixin
    login_url = 'login'
    redirect_field_name = None

    # Método para el cierre del día
    def cierre_dia(self, fecha, numero_pedidos, total_pollos, total_cachopos, total_ventas, overwrite=False):
        # Convertir la fecha a un objeto datetime en zona horaria actual
        try:
            fecha_cierre = timezone.make_aware(datetime.strptime(fecha, '%Y-%m-%d')).date()
            print(f"fecha cierre: {fecha_cierre}")
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Formato de fecha incorrecto.'})

        # Verificar si ya existe un resumen para esa fecha
        resumen_existente = ResumenVentas.objects.filter(fecha=fecha_cierre).first()

        if resumen_existente and not overwrite:
            return JsonResponse({'success': False, 'message': 'Ya existe un resumen para la fecha señalada'})

        # Si se desea sobreescribir, actualizar el resumen existente o crear uno nuevo
        if resumen_existente:
            resumen_existente.total_ventas = total_ventas
            resumen_existente.numero_pedidos = numero_pedidos
            resumen_existente.total_pollos = total_pollos
            resumen_existente.total_cachopos = total_cachopos
            resumen_existente.save()
            message = 'Resumen de ventas actualizado correctamente.'
        else:
            # Crear un nuevo ResumenVentas
            ResumenVentas.objects.create(
                fecha=fecha_cierre,
                total_ventas=total_ventas,
                numero_pedidos=numero_pedidos,
                total_pollos=total_pollos,
                total_cachopos=total_cachopos
            )
            message = 'Cierre de día realizado correctamente.'

        return JsonResponse({'success': True, 'message': message})


    # Filtro de fecha
    def get_queryset(self):
        queryset = super().get_queryset()
        fecha = self.request.GET.get('fecha')
        if fecha:
            try:
                # Convertir la fecha a un objeto datetime en zona horaria actual y sin hora
                fecha_inicio = timezone.make_aware(datetime.strptime(fecha, '%Y-%m-%d'))
                fecha_fin = fecha_inicio + timedelta(days=1) - timedelta(seconds=1)

                # Filtrar pedidos que estén dentro del rango del día
                queryset = queryset.filter(fecha_hora__range=(fecha_inicio, fecha_fin))
            except ValueError:
                print("Formato de fecha incorrecto")
        else:
            # Filtrar por la fecha actual en zona horaria local si no hay fecha proporcionada
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_today = today + timedelta(days=1) - timedelta(seconds=1)
            queryset = queryset.filter(fecha_hora__range=(today, end_of_today))

        return queryset

    # Total del pedido y cantidad de pedidos por intervalos horarios
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener la fecha del filtro o la fecha actual si no hay filtro
        fecha_filtro = self.request.GET.get('fecha')
        context['fecha'] = fecha_filtro or datetime.today().date().strftime('%Y-%m-%d')  # .date() para solo la parte de la fecha
        context['pedidos'] = self.get_queryset() 

        # Inicializamos el contador de pollos en el contexto
        total_pollos = Decimal('0.0')
        total_cachopos_ternera = Decimal('0.0')
        total_cachopos_pollo = Decimal('0.0')
        total_cachopos_lomo = Decimal('0.0')
        total_cachopos_degustacion = Decimal('0.0')

        # Inicializamos la variable total_ventas
        total_ventas = 0

        # Inicializamos un diccionario para contar los pedidos por intervalo
        intervalos = [('13:00', '13:15'),('13:15', '13:30'),('13:30', '13:45'), ('13:45', '14:00'), ('14:00', '14:15'), ('14:15', '14:30'), ('14:30', '14:45'), ('14:45', '15:00'), ('15:00', '15:15'), ('15:15', '15:30')]        
        conteo_pedidos_por_intervalo = {intervalo: 0 for intervalo in intervalos}

        # Calcular el precio total por cada pedido
        for pedido in context['pedidos']:
            # Inicializamos el total en 0
            total_precio = 0

            # Preparar una lista para los detalles de cada pedido
            pedido.detalles = []

            # Sumar precios de productos
            for detalle in pedido.pedidoproducto_set.all():
                precio_detalle = detalle.cantidad * detalle.producto.precio
                total_precio += detalle.cantidad * detalle.producto.precio
                pedido.detalles.append({
                    'nombre': detalle.producto.nombre,
                    'cantidad': detalle.cantidad,
                    'precio': precio_detalle
                })
                # Contar los pollos
                if detalle.producto.nombre.lower() == 'pollo asado':
                    total_pollos += detalle.cantidad
                elif detalle.producto.nombre.lower() == 'medio pollo asado':
                    total_pollos += Decimal('0.50') * detalle.cantidad 
                elif detalle.producto.nombre.lower() == 'cachopo ternera':
                    total_cachopos_ternera += detalle.cantidad
                elif detalle.producto.nombre.lower() == 'cachopo pollo':
                    total_cachopos_pollo += detalle.cantidad
                elif detalle.producto.nombre.lower() == 'cachopo lomo':
                    total_cachopos_lomo += detalle.cantidad

            # Sumar precios de menús
            for detalle in pedido.pedidomenu_set.all():
                precio_detalle = detalle.cantidad * detalle.menu.precio
                total_precio += precio_detalle
                pedido.detalles.append({
                    'nombre': detalle.menu.nombre,
                    'cantidad': detalle.cantidad,
                    'precio': precio_detalle
                })
                if detalle.menu.nombre.lower() == 'menú cachopo degustación':
                    total_cachopos_degustacion += detalle.cantidad * Decimal('1.00')
                    
                # Contar los pollos en los menús usando MenuProducto
                for menu_producto in detalle.menu.menuproducto_set.all():
                    nombre_producto = menu_producto.producto.nombre.lower()
                    # Contar los pollos
                    if 'pollo asado' in nombre_producto:
                        # El factor de cantidad es el número de menús, multiplicado por la cantidad de cada producto en el menú
                        if 'medio pollo' in nombre_producto:
                            total_pollos += Decimal('0.50') * detalle.cantidad * menu_producto.cantidad
                        else:
                            total_pollos += detalle.cantidad * menu_producto.cantidad
                    
                    # Contar los cachopos de ternera, pollo y lomo
                    if 'cachopo' in nombre_producto:
                        if 'ternera' in nombre_producto:
                            total_cachopos_ternera += detalle.cantidad * menu_producto.cantidad
                        elif 'pollo' in nombre_producto:
                            total_cachopos_pollo += detalle.cantidad * menu_producto.cantidad
                        elif 'lomo' in nombre_producto:
                            total_cachopos_lomo += detalle.cantidad * menu_producto.cantidad

            # Añadir el total a cada pedido
            pedido.total_precio = total_precio
            # Acumulamos el total de ventas
            total_ventas += total_precio

            # Obtener la hora del pedido
            hora_pedido = timezone.localtime(pedido.fecha_hora).time()  # Ajustamos a la zona horaria local

            # Contamos los pedidos por intervalo
            for i, (inicio, fin) in enumerate(intervalos):
                inicio_hora = datetime.strptime(inicio, '%H:%M').time()
                fin_hora = datetime.strptime(fin, '%H:%M').time()

                # Verificamos si la hora del pedido está dentro del intervalo
                if i == len(intervalos) - 1:  # Si es el último intervalo
                    if inicio_hora <= hora_pedido <= fin_hora:  # Permitimos la hora final también
                        conteo_pedidos_por_intervalo[(inicio, fin)] += 1
                        break  # Salimos del bucle una vez que encontramos el intervalo
                else:
                    if inicio_hora <= hora_pedido < fin_hora:  # Los demás intervalos son estrictos
                        conteo_pedidos_por_intervalo[(inicio, fin)] += 1
                        break  # Salimos del bucle una vez que encontramos el intervalo

        # Asignar total de pollos y cachopos al contexto
        context['total_pollos'] = total_pollos
        context['total_cachopos_ternera'] = total_cachopos_ternera
        context['total_cachopos_pollo'] = total_cachopos_pollo
        context['total_cachopos_lomo'] = total_cachopos_lomo
        context['total_cachopos_degustacion'] = total_cachopos_degustacion

        # Obtener inventarios
        inventario_pollo = Inventario.objects.filter(producto_id=1).first()
        if inventario_pollo:
            # Añadir inventario de pollo al contexto
            context['inventario_pollos'] = inventario_pollo
            # obtenemos el recuento de pollos restantes
            context['pollos_restantes'] = inventario_pollo.cantidad_disponible - total_pollos
        else:
            context['inventario_pollos'] = None
            context['pollos_restantes'] = 0

        # añadimos el total de ventas  al contexto
        context['total_ventas'] = total_ventas 

        # Añadir el conteo de pedidos por intervalo al contexto
        context['conteo_pedidos_por_intervalo'] = conteo_pedidos_por_intervalo 

        return context

    def post(self, request, *args, **kwargs):
        # Asegúrate de que estás accediendo a request.body correctamente
        try:
            data = json.loads(request.body)  # Cargar los datos JSON enviados
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Error al procesar los datos.'})

        # Manejo de las acciones
        accion = data.get('accion')
        pedido_id = data.get('pedido_id')

        # Asegúrate de que estás accediendo a request.POST correctamente
        if accion == 'eliminar':
            if pedido_id:
                pedido = get_object_or_404(Pedido, id=pedido_id)
                pedido.delete()
                return JsonResponse({'success': True, 'message': 'Pedido eliminado correctamente.'})

        elif accion in ['marcar_entregado', 'desmarcar_entregado']:
            if pedido_id:
                pedido = get_object_or_404(Pedido, id=pedido_id)
                # Actualiza el estado de entrega
                if data['accion'] == 'marcar_entregado':
                    pedido.entregado = True
                else:  # 'desmarcar_entregado'
                    pedido.entregado = False
                
                # Guarda los cambios en la base de datos
                try:
                    pedido.save()
                    return JsonResponse({'success': True, 'message': 'Estado de entrega actualizado.'})
                except Exception as e:
                    print(f'Error al guardar el pedido: {e}')  # Para depuración
                    return JsonResponse({'success': False, 'message': 'Error al actualizar el estado del pedido.'})

            
        # Acción para cierre del día
        elif accion == 'cierre_dia':
            fecha = data.get('fecha')
            numero_pedidos = data.get('numero_pedidos')
            total_pollos = data.get('total_pollos')
            total_cachopos = data.get('total_cachopos')
            total_ventas = data.get('totalVentas')
            overwrite = data.get('overwrite', False)  # Valor por defecto es False
            print(f"fecha: {fecha}")
            return self.cierre_dia(fecha, numero_pedidos, total_pollos, total_cachopos, total_ventas, overwrite)
        
        return JsonResponse({'success': False, 'message': 'No se pudo procesar la solicitud.'})

# Crear un nuevo pedido
class PedidoCreateView(CreateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'asador/pedidos/crear_pedido.html'
    success_url = reverse_lazy('lista_pedidos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.all().order_by('categoria', 'nombre')
        context['menus'] = Menu.objects.all().order_by('nombre')
        return context

    def form_valid(self, form):
        # Guardar el pedido
        pedido = form.save()
        print(f"Fecha y hora del pedido guardado: {pedido.fecha_hora}")
        # Procesar productos asociados
        i = 0
        while True:
            producto_id = self.request.POST.get(f'productos[{i}][producto]')
            cantidad = self.request.POST.get(f'productos[{i}][cantidad]')
            
            if producto_id is None or cantidad is None:
                break  # Salir del bucle si no hay más productos

            if producto_id and cantidad:
                producto = get_object_or_404(Producto, id=producto_id)
                PedidoProducto.objects.create(pedido=pedido, producto=producto, cantidad=int(cantidad))
            
            i += 1  # Incrementar el índice para la próxima iteración

        # Procesar menús asociados
        i = 0
        while True:
            menu_id = self.request.POST.get(f'menus[{i}][menu]')
            cantidad = self.request.POST.get(f'menus[{i}][cantidad]')

            if menu_id is None or cantidad is None:
                break  # Salir del bucle si no hay más menús

            if menu_id and cantidad:
                menu = get_object_or_404(Menu, id=menu_id)
                PedidoMenu.objects.create(pedido=pedido, menu=menu, cantidad=int(cantidad))
            
            i += 1  # Incrementar el índice para la próxima iteración

        return super().form_valid(form)


# Editar un pedido existente
class PedidoUpdateView(UpdateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'asador/pedidos/editar_pedido.html'
    success_url = reverse_lazy('lista_pedidos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.all().order_by('categoria', 'nombre')
        context['menus'] = Menu.objects.all().order_by('nombre')
        context['pedido_productos'] = PedidoProducto.objects.filter(pedido=self.object)
        context['pedido_menus'] = PedidoMenu.objects.filter(pedido=self.object)
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        initial['fecha_hora'] = self.object.fecha_hora.astimezone(timezone.get_current_timezone()).replace(tzinfo=None).isoformat()
        return initial

    def form_valid(self, form):
        # Guardar el pedido
        pedido = form.save()

        # Eliminar los productos y menús existentes antes de agregar los nuevos
        PedidoProducto.objects.filter(pedido=pedido).delete()
        PedidoMenu.objects.filter(pedido=pedido).delete()

        # Procesar productos asociados
        i = 0
        while True:
            producto_id = self.request.POST.get(f'productos[{i}][producto]')
            cantidad = self.request.POST.get(f'productos[{i}][cantidad]')
            
            if producto_id is None or cantidad is None:
                break  # Salir del bucle si no hay más productos

            if producto_id and cantidad:
                producto = get_object_or_404(Producto, id=producto_id)
                PedidoProducto.objects.create(pedido=pedido, producto=producto, cantidad=int(cantidad))
            
            i += 1  # Incrementar el índice para la próxima iteración

        # Procesar menús asociados
        i = 0
        while True:
            menu_id = self.request.POST.get(f'menus[{i}][menu]')
            cantidad = self.request.POST.get(f'menus[{i}][cantidad]')

            if menu_id is None or cantidad is None:
                break  # Salir del bucle si no hay más menús

            if menu_id and cantidad:
                menu = get_object_or_404(Menu, id=menu_id)
                PedidoMenu.objects.create(pedido=pedido, menu=menu, cantidad=int(cantidad))
            
            i += 1  # Incrementar el índice para la próxima iteración

        return super().form_valid(form)
