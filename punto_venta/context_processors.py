"""Context processor."""

# SourceStock - Api
from api.services import get_dolar_value


# ------ SERVICES ------ #

def sample_context_processor(request):
    """Pasar el price del dolar por contexto para el navbar."""

    return {'dolar':get_dolar_value()[1]}