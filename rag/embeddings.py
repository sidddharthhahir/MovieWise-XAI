import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from core.models import Movie


logger = logging.getLogger(__name__)

class Store:
    def __init__(self):
        self.vec = TfidfVectorizer(max_features=20000, ngram_range=(1, 2), stop_words='english')
        self.nn = None
        self.ids = []
        self.X = None
    
    def build(self):
        """Build the TF-IDF index from all movies."""
        texts = []
        ids = []
        
        for m in Movie.objects.all():
            text = (m.title or '') + ' ' + (m.overview or '')
            texts.append(text)
            ids.append(m.id)
        
        if not texts:
            logger.warning("No movies found for RAG indexing")
            return
        
        try:
            self.X = self.vec.fit_transform(texts)
            self.nn = NearestNeighbors(n_neighbors=min(10, len(texts)), metric='cosine')
            self.nn.fit(self.X)
            self.ids = ids
            logger.info("RAG index built with %s movies", len(texts))
        except Exception as e:
            logger.exception("RAG index build failed: %s", e)
    
    def search(self, q, k=5):
        """Search for similar movies using cosine similarity."""
        if not self.nn:
            self.build()
        
        if not self.nn:
            return []
        
        try:
            qv = self.vec.transform([q])
            dist, idx = self.nn.kneighbors(qv, n_neighbors=min(k, len(self.ids)))
            return [(self.ids[i], 1 - float(d)) for i, d in zip(idx[0], dist[0])]
        except Exception as e:
            logger.exception("RAG search failed: %s", e)
            return []
    
    def get_context_for_movie(self, movie_id, k=3):
        """Return similar movies with lightweight metadata."""
        try:
            movie = Movie.objects.get(id=movie_id)
            query = f"{movie.title} {movie.overview or ''}"
            hits = self.search(query, k=k + 1)
            hits = [(mid, score) for mid, score in hits if mid != movie_id][:k]
            
            if not hits:
                return []
            
            movie_ids = [mid for mid, _ in hits]
            movies = {m.id: m for m in Movie.objects.filter(id__in=movie_ids)}
            
            context = []
            for mid, score in hits:
                if mid in movies:
                    m = movies[mid]
                    context.append({
                        'title': m.title,
                        'overview': m.overview,
                        'vote': m.vote,
                        'similarity_score': round(score, 3)
                    })
            
            return context
        except Exception as e:
            logger.exception("Context retrieval failed: %s", e)
            return []
    
    def get_user_preference_context(self, user_id, k=5):
        """Return recommendation context from the user's liked movies."""
        try:
            from core.models import Rating
            
            user_ratings = Rating.objects.filter(user_id=user_id, value__gte=4)
            if not user_ratings.exists():
                return []
            
            liked_movies = [r.movie for r in user_ratings[:5]]
            query_parts = []
            for movie in liked_movies:
                query_parts.append(f"{movie.title} {movie.overview or ''}")
            
            query = " ".join(query_parts)
            hits = self.search(query, k=k)
            
            movie_ids = [mid for mid, _ in hits]
            movies = {m.id: m for m in Movie.objects.filter(id__in=movie_ids)}
            
            context = []
            for mid, score in hits:
                if mid in movies:
                    m = movies[mid]
                    context.append({
                        'title': m.title,
                        'vote': m.vote,
                        'similarity_score': round(score, 3)
                    })
            
            return context
        except Exception as e:
            logger.exception("User preference context failed: %s", e)
            return []

store = Store()

def get_rag_context(movie_id=None, user_id=None, k=3):
    """Unified helper for movie or user-driven RAG context."""
    if movie_id:
        return store.get_context_for_movie(movie_id, k=k)
    elif user_id:
        return store.get_user_preference_context(user_id, k=k)
    else:
        return []