from erp.models import Article, Client

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
        query = Client.objects.filter(nombre__icontains=infForm['name'],
                                        dni__icontains=infForm['dni'])
    else:
        query = Client.objects.filter(nombre__icontains=infForm['name'])
    
    return query