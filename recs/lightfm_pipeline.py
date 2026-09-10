import logging
import os

import joblib
import numpy as np
from django.conf import settings
from core.models import Movie, Rating
from django.contrib.auth.models import User
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


logger = logging.getLogger(__name__)
ART=os.path.join(settings.MODEL_DIR,'lightfm_artifacts.pkl')

def content_based_recommendations(user_id, k=12):
    """Content-based recommendations using movie overviews and user preferences."""
    all_movies = list(Movie.objects.all())
    if not all_movies:
        return []
    
    user_ratings = Rating.objects.filter(user_id=user_id)
    if not user_ratings:
        return sorted(all_movies, key=lambda m: (m.vote or 0) * 0.6 + (m.popularity or 0) * 0.4, reverse=True)[:k]
    
    movie_texts = []
    for movie in all_movies:
        text = f"{movie.title} {movie.overview or ''}"
        movie_texts.append(text)
    
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(movie_texts)
    
    preferred_movies = [r.movie for r in user_ratings if r.value >= 4]
    
    if not preferred_movies:
        return sorted(all_movies, key=lambda m: (m.vote or 0) * 0.6 + (m.popularity or 0) * 0.4, reverse=True)[:k]
    
    preferred_indices = [all_movies.index(movie) for movie in preferred_movies if movie in all_movies]
    movie_scores = {}
    
    for i, movie in enumerate(all_movies):
        if movie in preferred_movies:
            continue

        similarities = []
        for pref_idx in preferred_indices:
            similarity = cosine_similarity(tfidf_matrix[i], tfidf_matrix[pref_idx])[0][0]
            similarities.append(similarity)
        
        avg_similarity = np.mean(similarities) if similarities else 0

        quality_score = (movie.vote or 0) * 0.6 + (movie.popularity or 0) * 0.4
        final_score = avg_similarity * quality_score
        movie_scores[movie.id] = final_score

    sorted_movies = sorted(all_movies, key=lambda m: movie_scores.get(m.id, 0), reverse=True)
    return sorted_movies[:k]

def _train_fallback():
    movies=list(Movie.objects.all())
    if not movies:
        joblib.dump({'model':None,'items':[],'mode':'fallback'}, ART); return ART
    maxp=max([m.popularity or 0 for m in movies]) or 1.0
    scores={m.id: 0.6*((m.vote or 0)/10.0) + 0.4*((m.popularity or 0)/maxp) for m in movies}
    joblib.dump({'model':scores,'items':[m.id for m in movies],'mode':'fallback'}, ART); return ART
def train_and_save(epochs=8):
    try:
        from lightfm import LightFM
        from lightfm.data import Dataset
    except Exception as e:
        logger.warning("LightFM import failed, using fallback: %s", e)
        return _train_fallback()
    
    users=list(User.objects.values_list('id', flat=True)) or [1]
    items=list(Movie.objects.values_list('id', flat=True))
    
    if not items:
        logger.warning("No movies found in database, using fallback model")
        return _train_fallback()

    logger.info("Training recommender with %s users and %s items", len(users), len(items))
    
    ds=Dataset(); ds.fit(users, items)
    
    if Rating.objects.exists():
        logger.info("Using %s existing ratings", Rating.objects.count())
        triples=((r.user_id or 1, r.movie_id, float(r.value)) for r in Rating.objects.all())
    else:
        logger.info("No ratings found, using popularity as proxy interactions")
        triples=((1, m.id, float(m.popularity or 1.0)) for m in Movie.objects.all())
    
    try:
        (mat,_)=ds.build_interactions(triples)
    except Exception as e:
        logger.exception("Failed to build interaction matrix: %s", e)
        return _train_fallback()
    
    try:
        model=LightFM(loss='warp')
        model.fit(mat, epochs=epochs, num_threads=2)
    except Exception as e:
        logger.exception("LightFM training failed: %s", e)
        return _train_fallback()

    joblib.dump({'model':model,'items':items,'mode':'lightfm'}, ART)
    logger.info("Saved LightFM model to %s", ART)
    return ART
def load_artifacts():
    if not os.path.exists(ART): train_and_save(epochs=4)
    return joblib.load(ART)
def topn_for_user(user_id=1, k=12):
    """Get top recommendations using LightFM when available."""
    artifacts = load_artifacts()
    mode = artifacts.get('mode', 'fallback')

    if mode == 'lightfm' and artifacts.get('model') is not None:
        try:
            model = artifacts['model']
            items = artifacts['items']

            if not items:
                return []

            all_users = list(User.objects.values_list('id', flat=True)) or [1]
            if user_id not in all_users:
                return content_based_recommendations(user_id, k)

            user_index = all_users.index(user_id)

            item_indices = np.arange(len(items))

            scores = model.predict(
                user_ids=np.repeat(user_index, len(items)),
                item_ids=item_indices
            )

            order = np.argsort(-scores)[:k]
            chosen_db_ids = [items[i] for i in order]

            movies = list(Movie.objects.filter(id__in=chosen_db_ids))
            movies.sort(key=lambda m: chosen_db_ids.index(m.id))
            return movies

        except Exception as e:
            logger.exception("LightFM prediction failed, using content-based fallback: %s", e)
            return content_based_recommendations(user_id, k)

    elif mode == 'fallback' and artifacts.get('model') is not None:
        try:
            scores = artifacts['model']
            items = artifacts['items']
            if not items:
                return []
            sorted_items = sorted(items, key=lambda i: scores.get(i, 0), reverse=True)
            chosen = sorted_items[:k]
            movies = list(Movie.objects.filter(id__in=chosen))
            movies.sort(key=lambda m: chosen.index(m.id))
            return movies
        except Exception as e:
            logger.exception("Fallback prediction failed, using content-based mode: %s", e)
            return content_based_recommendations(user_id, k)

    return content_based_recommendations(user_id, k)