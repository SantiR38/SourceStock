""" Messages views."""
from django.shortcuts import render
from django.views.generic import TemplateView


class TimesUpView(TemplateView):
    """
    Shows a message when a demo has expired,
    and is redirected from the middleware.
    """
    template_name = 'messages/simple.html'

    def get_context_data(self, **kwargs):
        """Context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = "Tiempo finalizado"
        context['titulo'] = "Tiempo finalizado"
        context['message'] = ("Su versión de prueba ha expirado. "
            "Si desea obtener el servicio completo, "
            "comuníquese con el desarrollador.")
        context['contact'] = ("Santiago Rodríguez - "
            "Tel: +54 9 358 516-3434 - E-mail: santirodriguez38@gmail.com")
        return context
