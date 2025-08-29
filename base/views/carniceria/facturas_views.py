from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from base.models import Factura, FacturaProducto
from base.forms import FacturaForm, FacturaProductoFormSet
from django.db import transaction
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.template.loader import get_template
import pdfkit
from django.conf import settings
from bs4 import BeautifulSoup

class FacturaListView(ListView):
    model = Factura
    template_name = 'carniceria/facturas/lista_facturas.html'
    context_object_name = 'facturas'
    ordering = ['numero_factura']

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

        # Filtrar las facturas por el rango de fechas si es válido
        if fecha_inicio and fecha_fin:
            context['facturas'] = Factura.objects.select_related('cliente').filter(fecha_emision__range=(fecha_inicio, fecha_fin)).order_by('-fecha_emision')
        else:
            context['facturas'] = Factura.objects.select_related('cliente').all().order_by('-fecha_emision')

        # Añadir las fechas al contexto para el formulario
        context['fecha_inicio'] = fecha_inicio_str if fecha_inicio_str else fecha_inicio.strftime('%Y-%m-%d')
        context['fecha_fin'] = fecha_fin_str if fecha_fin_str else fecha_fin.strftime('%Y-%m-%d')

        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('accion') == 'eliminar':
            factura_id = request.POST.get('factura_id')
            if factura_id:
                factura = get_object_or_404(Factura, id=factura_id)
                factura.delete()
                return JsonResponse({'success': True, 'message': 'Factura eliminada correctamente.'})
        return super().get(request, *args, **kwargs)

from django.db import transaction

class FacturaCreateView(CreateView):
    model = Factura
    form_class = FacturaForm
    template_name = 'carniceria/facturas/crear_factura.html'
    success_url = reverse_lazy('lista_facturas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['productos'] = FacturaProductoFormSet(self.request.POST)
        else:
            context['productos'] = FacturaProductoFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        productos_formset = context['productos']

        if form.is_valid() and productos_formset.is_valid():
            with transaction.atomic():
                print("Guardando la instancia de Factura...")
                self.object = form.save()
                print("Factura guardada con ID:", self.object.pk)

                # Establecer la instancia de Factura en el formset y guardar los productos
                productos_formset.instance = self.object
                productos_formset.save()
                print("Productos guardados para la Factura con ID:", self.object.pk)

                # Verificar los productos guardados
                for producto_form in productos_formset:
                    if producto_form.instance.pk:
                        print(f"Producto guardado con ID: {producto_form.instance.pk}, descripción: {producto_form.instance.descripcion}")
                    else:
                        print("Producto no se guardó correctamente.")
                        print("Errores en el form de producto:", producto_form.errors)
                        print("Datos del form de producto:", producto_form.cleaned_data)
                
                # Imprimir datos recibidos para depuración adicional
                print("Datos del formset de productos recibidos:", self.request.POST)

            return super().form_valid(form)
        else:
            print("Formulario inválido o formset inválido.")
            if not form.is_valid():
                print("Errores en el formulario de Factura:", form.errors)
            if not productos_formset.is_valid():
                print("Errores en el formset de productos:", productos_formset.errors)
                for producto_form in productos_formset:
                    print("Errores en el form de producto:", producto_form.errors)
                    print("Datos del form de producto:", producto_form.cleaned_data)
            return self.render_to_response(self.get_context_data(form=form))

class FacturaUpdateView(UpdateView):
    model = Factura
    form_class = FacturaForm
    template_name = 'carniceria/facturas/editar_factura.html'
    success_url = reverse_lazy('lista_facturas')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['productos'] = FacturaProductoFormSet(self.request.POST, instance=self.object)
            print("POST Data:", self.request.POST)
        else:
            context['productos'] = FacturaProductoFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        productos_formset = context['productos']

        if form.is_valid() and productos_formset.is_valid():
            with transaction.atomic():
                self.object = form.save()
                productos_formset.instance = self.object
                productos_formset.save()
                
                # Log productos eliminados y eliminarlos de la base de datos
                for producto_form in productos_formset.deleted_forms:
                    if producto_form.instance.pk:
                        print("Deleting product:", producto_form.instance.pk)
                        producto_form.instance.delete()

                # Agregar logs después de la validación y guardado
                print("Form Data:", form.cleaned_data)
                print("Product Formset Data:", [producto_form.cleaned_data for producto_form in productos_formset.forms if producto_form.cleaned_data])
                print("Deleted Products:", [producto_form.instance.pk for producto_form in productos_formset.deleted_forms])

            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class FacturaPreviewView(DetailView):
    model = Factura
    template_name = 'carniceria/facturas/previsualizar_factura.html'
    context_object_name = 'factura'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener la factura actual
        factura = self.get_object()

        # Obtener el cliente relacionado
        cliente = factura.cliente

        # Obtener los productos relacionados con la factura
        productos = FacturaProducto.objects.filter(factura=factura)

        # Pasar los datos al contexto
        context['cliente'] = cliente
        context['productos'] = productos
        context['empresa'] = {
            'nombre': factura.nombre_emisor,
            'telefono': factura.telefono_empresa,
            'email': factura.email_empresa,
            'direccion': factura.direccion_emisor,
            'cif_nif': factura.cif_nif_emisor
        }
        context['totales'] = {
            'neto': factura.total_neto,
            'iva': factura.total_iva,
            'total': factura.total
        }

        return context

    def post(self, request, *args, **kwargs):
        factura = self.get_object()
        productos = FacturaProducto.objects.filter(factura=factura)

        # Contexto para el template
        context = {
            'factura': factura,
            'cliente': factura.cliente,
            'productos': productos,
            'empresa': {
                'nombre': factura.nombre_emisor,
                'telefono': factura.telefono_empresa,
                'email': factura.email_empresa,
                'direccion': factura.direccion_emisor,
                'cif_nif': factura.cif_nif_emisor
            },
            'totales': {
                'neto': factura.total_neto,
                'iva': factura.total_iva,
                'total': factura.total
            },
        }

        # Renderizar el template HTML
        template = get_template(self.template_name)
        html = template.render(context)

        # Usar BeautifulSoup para extraer el div "factura-container"
        soup = BeautifulSoup(html, 'html.parser')
        factura_container = soup.find('div', class_='factura-container')

        if not factura_container:
            return HttpResponse('Error: No se encontró el contenido de la factura.', status=400)

        # Ajustar las rutas relativas de las imágenes
        for img in factura_container.find_all('img'):
            src = img['src']
            if src.startswith('/'):  # Convertir rutas relativas a absolutas
                img['src'] = request.build_absolute_uri(src)

        # Convertir el div extraído a HTML
        factura_html = f"""
        <html>
            <head>
                <style>
                    html, body {{
                        margin: 0;
                        padding: 0;
                        width: 100%;
                        height: 100%;
                    }}
                </style>
                <link rel="stylesheet" href="{request.build_absolute_uri(settings.STATIC_URL + 'styles/carniceria/facturas/facturas.css')}">
            </head>
            <body>
                {factura_container}
            </body>
        </html>
        """

        # Configuración de pdfkit
        options = {
            'page-size': 'A4',
            'margin-top': '0mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'encoding': 'UTF-8',
            'enable-local-file-access': None,  # Habilitar acceso a archivos locales
        }

        # Generar el PDF desde el div renderizado
        pdf = pdfkit.from_string(
            factura_html,
            False,
            options=options,
            configuration=pdfkit.configuration(wkhtmltopdf=settings.PDFKIT_WKHTMLTOPDF)
        )

        # Enviar el PDF como respuesta HTTP
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Factura_Pettisso_{factura.numero_factura}.pdf"'

        return response
