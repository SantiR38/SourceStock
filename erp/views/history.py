from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django.views.generic import DetailView
from django.views.generic.dates import MonthArchiveView

from erp.models import Venta, DetalleVenta, Entrada, DetalleEntrada


class HistorialMixin(MonthArchiveView): # Clase padre de las dos siguientes.
    date_field = 'fecha'
    paginate_by = 15
    allow_future = True
    allow_empty = True
    template_name = 'erp/transaction_archive_month.html'

class HistorialDeVenta(HistorialMixin):
    queryset = Venta.objects.all().order_by('-fecha', '-id')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Historial de ventas"
        context['url'] = "historial_de_venta"
        return context

class HistorialDeCompra(HistorialMixin):
    queryset = Entrada.objects.all()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Historial de compras"
        context['url'] = "historial_de_compra"
        return context

class DetalleDeCompra(DetailView):
    template_name = "erp/detalle_de_operacion.html"

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Entrada, id=id_)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Detalle de compra"
        context['subtitulo'] = "Compra realizada"
        context['persona'] = "Proveedor"
        context['elementos_vendidos'] = DetalleEntrada.objects.filter(id_entrada=self.kwargs.get("id"))
        return context
    
    def post(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        DetalleEntrada.give_product_back(id_)
        DetalleEntrada.objects.filter(id_entrada=id_).delete()
        Entrada.objects.get(id=id_).delete()
        return HttpResponseRedirect('/historial_de_compra/2020/01/')

class DetalleDeVenta(DetailView):
    pass
