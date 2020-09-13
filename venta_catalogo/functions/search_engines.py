from erp.models import Article, Cliente

def search_articles(infForm):
    if infForm['codigo'] != None:
        query = Article.objects.filter(seccion__icontains=infForm['seccion'],
                                        descripcion__icontains=infForm['descripcion'],
                                        marca__icontains=infForm['marca'],
                                        codigo__icontains=infForm['codigo'])
    else:
        query = Article.objects.filter(seccion__icontains=infForm['seccion'],
                                        descripcion__icontains=infForm['descripcion'],
                                        marca__icontains=infForm['marca'])

    return query

def search_clients(infForm):
    if infForm['dni'] != None:
        query = Cliente.objects.filter(nombre__icontains=infForm['nombre'],
                                        dni__icontains=infForm['dni'])
    else:
        query = Cliente.objects.filter(nombre__icontains=infForm['nombre'])
    
    return query