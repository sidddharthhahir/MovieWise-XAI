from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import Movie
from .embeddings import store
@api_view(['GET'])
def qa(request):
    q=request.GET.get('q',''); hits=store.search(q, k=5)
    movies={m.id:m for m in Movie.objects.filter(id__in=[i for i,_ in hits])}
    context=' '.join((movies[i].overview or movies[i].title or '') for i,_ in hits)
    ans=(context[:700]+'...') if len(context)>700 else context
    return Response({"question":q,"answer":ans,"hits":[{"id":i,"title":movies[i].title,"score":s} for i,s in hits]})
