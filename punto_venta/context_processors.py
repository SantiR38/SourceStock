"""Context processor."""

# SourceStock - Api
from api.models import PrecioDolar
from api.services import get_dolar_value

# ------ SERVICES ------ #

def sample_context_processor(request):
    """Pasar el precio del dolar por contexto para el navbar."""
    try:
        dolar_value = get_dolar_value()[1]
    except TypeError:
        dolar_value = PrecioDolar.cotizacion_venta()
    return {'dolar':dolar_value}