from django.shortcuts import render

from .services import get_dolar_value


def dolar(requests):
    context = {
        'compra': get_dolar_value()[0],
        'venta': get_dolar_value()[1]
    }
    return render(requests, 'api_dolar/hello_user.html', context)
