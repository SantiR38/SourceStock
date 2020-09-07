from erp.models import Article

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