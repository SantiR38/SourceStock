import requests

def generate_request(url, params={}):
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()

def get_dolar_value(params={}):
    response = generate_request('https://www.dolarsi.com/api/api.php?type=valoresprincipales', params)[0]
    if response:
       dolar_value = response.get('casa')
       return [dolar_value.get('compra'), dolar_value.get('venta')]

    return ''
