from erp.models import Article, Cliente

def search_articles(infForm):
    if infForm['code'] != None:
        query = Article.objects.filter(seccion__icontains=infForm['section'],
                                        description__icontains=infForm['description'],
                                        marca__icontains=infForm['brand'],
                                        code__icontains=infForm['code'])
    else:
        query = Article.objects.filter(seccion__icontains=infForm['section'],
                                        description__icontains=infForm['description'],
                                        marca__icontains=infForm['brand'])

    return query

def search_clients(infForm):
    if infForm['dni'] != None:
        query = Cliente.objects.filter(nombre__icontains=infForm['nombre'],
                                        dni__icontains=infForm['dni'])
    else:
        query = Cliente.objects.filter(nombre__icontains=infForm['nombre'])
    
    return query