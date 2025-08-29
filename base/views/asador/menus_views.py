from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.http import JsonResponse
from base.forms import MenuForm
from base.models import Menu, MenuProducto, Producto

class MenuListView(ListView):
    model = Menu
    template_name = 'asador/menus/lista_menus.html'
    context_object_name = 'menus'
    ordering = ['nombre']
    
    def post(self, request, *args, **kwargs):
        if request.POST.get('accion') == 'eliminar':
            menu_id = request.POST.get('menu_id')
            if menu_id:
                menu = get_object_or_404(Menu, id=menu_id)
                menu.delete()
                return JsonResponse({'success': True, 'message': 'Menú eliminado correctamente.'})
        return super().get(request, *args, **kwargs)


class MenuCreateView(CreateView):
    model = Menu
    form_class = MenuForm
    template_name = 'asador/menus/crear_menu.html'
    success_url = reverse_lazy('lista_menus')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.all().order_by('categoria', 'nombre')  # Pasar los productos al contexto
        return context

    def form_valid(self, form):
        # Guardar el menú
        menu = form.save()

        # Procesar productos asociados
        i = 0
        while True:
            producto_id = self.request.POST.get(f'productos[{i}][producto]')
            cantidad = self.request.POST.get(f'productos[{i}][cantidad]')

            if producto_id is None or cantidad is None:
                break  # Salir del bucle si no hay más productos

            if producto_id and cantidad:
                producto = get_object_or_404(Producto, id=producto_id)
                MenuProducto.objects.create(menu=menu, producto=producto, cantidad=int(cantidad))

            i += 1  # Incrementar el índice para la próxima iteración

        return super().form_valid(form)


class MenuUpdateView(UpdateView):
    model = Menu
    form_class = MenuForm
    template_name = 'asador/menus/editar_menu.html'
    success_url = reverse_lazy('lista_menus')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.all().order_by('categoria', 'nombre')  # Pasar los productos al contexto
        menu_productos = MenuProducto.objects.filter(menu=self.object)
        context['menu_productos'] = menu_productos  # Productos asociados al menú
        return context

    def form_valid(self, form):
        # Guardar el menú
        menu = form.save()

        # Limpiar productos existentes antes de agregar los nuevos
        MenuProducto.objects.filter(menu=menu).delete()

        # Procesar productos asociados
        i = 0
        while True:
            producto_id = self.request.POST.get(f'productos[{i}][producto]')
            cantidad = self.request.POST.get(f'productos[{i}][cantidad]')

            if producto_id is None or cantidad is None:
                break  # Salir del bucle si no hay más productos

            if producto_id and cantidad:
                producto = get_object_or_404(Producto, id=producto_id)
                MenuProducto.objects.create(menu=menu, producto=producto, cantidad=int(cantidad))

            i += 1  # Incrementar el índice para la próxima iteración

        return super().form_valid(form)