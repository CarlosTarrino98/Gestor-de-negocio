from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.http import JsonResponse
from base.models import Producto

class ProductoListView(ListView):
    model = Producto
    template_name = 'asador/productos/lista_productos.html'
    context_object_name = 'productos'
    
    def get_queryset(self):
        # Ordenar por 'categoria' y luego alfabéticamente por 'nombre'
        return Producto.objects.all().order_by('categoria', 'nombre')

    def post(self, request, *args, **kwargs):
        if request.POST.get('accion') == 'eliminar':
            producto_id = request.POST.get('producto_id')
            if producto_id:
                producto = get_object_or_404(Producto, id=producto_id)
                producto.delete()
                return JsonResponse({'success': True, 'message': 'Producto eliminado correctamente.'})
        return super().get(request, *args, **kwargs)


class ProductoCreateView(CreateView):
    model = Producto
    template_name = 'asador/productos/crear_producto.html'
    fields = ['nombre', 'categoria', 'precio']
    success_url = reverse_lazy('lista_productos')


class ProductoUpdateView(UpdateView):
    model = Producto
    template_name = 'asador/productos/editar_producto.html'
    fields = ['nombre', 'categoria', 'precio']
    success_url = reverse_lazy('lista_productos')