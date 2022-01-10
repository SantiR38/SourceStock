from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from erp.models import Venta, DetalleVenta, Entrada, DetalleEntrada


class DetalleDeCompra(DetailView):
    template_name = "erp/detalle_de_operacion.html"

    def get_object(self):
        return get_object_or_404(Entrada, id=self.kwargs.get("id"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Detalle de compra"
        context['subtitulo'] = "Compra realizada"
        context['persona'] = "Proveedor"
        context['elementos_vendidos'] = DetalleEntrada.objects.filter(
            id_entrada=self.kwargs.get("id"))

        return context
    
    def post(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        DetalleEntrada.give_product_back()
        DetalleEntrada.objects.filter(id_entrada=id_).delete()
        Entrada.objects.get(id=id_).delete()

        return HttpResponseRedirect('/historial_compras/')


class DetalleDeVenta(DetailView):
    template_name = "erp/detalle_de_operacion.html"

    def get_object(self):
        return get_object_or_404(Venta, id=self.kwargs.get("id"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Detalle de venta"
        context['subtitulo'] = "Venta realizada"
        context['persona'] = "Cliente"
        context['elementos_vendidos'] = DetalleVenta.objects.filter(
            id_venta=self.kwargs.get("id"))

        return context
    
    def post(self, request, *args, **kwargs):
        id_ = self.kwargs.get("id")
        DetalleVenta.take_product_back(id_)
        DetalleVenta.objects.filter(id_venta=id_).delete()
        Venta.objects.filter(id=id_).delete()

        return HttpResponseRedirect('/historial_ventas/')
