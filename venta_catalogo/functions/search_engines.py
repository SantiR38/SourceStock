from erp.models import Article

def search_articles(infForm):
    query = Article.objects.filter(codigo=infForm['codigo'])