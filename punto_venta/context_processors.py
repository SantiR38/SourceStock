# Context processor
from api.services import get_dolar_value

def sample_context_processor(request):
    """Pasar el precio del dolar por contexto para el navbar"""

    return {'dolar':get_dolar_value()[1]}