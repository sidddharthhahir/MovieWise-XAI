from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from core.models import Movie
class Store:
    def __init__(self): self.vec=TfidfVectorizer(max_features=20000, ngram_range=(1,2)); self.nn=None; self.ids=[]
    def build(self):
        texts=[]; ids=[]
        for m in Movie.objects.all(): texts.append((m.title or '')+' '+(m.overview or '')); ids.append(m.id)
        if not texts: return
        X=self.vec.fit_transform(texts); from sklearn.neighbors import NearestNeighbors
        self.nn=NearestNeighbors(n_neighbors=5, metric='cosine').fit(X); self.X=X; self.ids=ids
    def search(self,q,k=5):
        if not self.nn: self.build()
        if not self.nn: return []
        qv=self.vec.transform([q]); dist,idx=self.nn.kneighbors(qv, n_neighbors=min(k,len(self.ids)))
        return [(self.ids[i], 1-float(d)) for i,d in zip(idx[0], dist[0])]
store=Store()
