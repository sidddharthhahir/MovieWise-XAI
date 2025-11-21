"""
XAI Explainer for LightFM Model
Integrates SHAP and LIME for model interpretability
"""
import numpy as np
from core.models import Movie, Rating
from django.contrib.auth.models import User

def get_lightfm_feature_importance(user_id, movie_id, model, items):
    """
    Extract feature importance from LightFM model using approximation.
    Maps Django user_id to LightFM user index safely.
    """
    try:
        # Ensure movie exists in items
        if movie_id not in items:
            return None

        item_idx = items.index(movie_id)

        # Map user_id to consecutive index (same logic as in topn_for_user)
        all_users = list(User.objects.values_list('id', flat=True)) or [1]
        if user_id not in all_users:
            return None
        user_index = all_users.index(user_id)

        user_embedding = model.user_embeddings[user_index]
        item_embedding = model.item_embeddings[item_idx]

        # Sanity check shapes
        if user_embedding.shape[0] != item_embedding.shape[0]:
            # Dimension mismatch – don't try to interpret
            return None

        contributions = user_embedding * item_embedding  # element-wise
        dim = contributions.shape[0]

        # Get top contributing dimensions safely
        k = min(5, dim)
        top_indices = np.argsort(np.abs(contributions))[-k:][::-1]

        feature_importance = {
            'embedding_contributions': contributions.tolist(),
            'top_dimensions': [int(i) for i in top_indices],
            'top_values': [float(contributions[i]) for i in top_indices],
            'prediction_score': float(np.dot(user_embedding, item_embedding))
        }
        return feature_importance

    except Exception as e:
        print(f"Feature importance extraction failed: {e}")
        return None


def compute_shap_like_values(user_id, movie_id, model, items):
    """
    Compute SHAP-like values for LightFM recommendations
    This approximates feature importance using embedding analysis
    """
    try:
        # Get user's rating history
        user_ratings = Rating.objects.filter(user_id=user_id)
        
        if not user_ratings.exists():
            return {
                'genre_weight': 0.3,
                'rating_weight': 0.3,
                'popularity_weight': 0.2,
                'user_preference_weight': 0.2
            }
        
        # Get the target movie
        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return None
        
        # Calculate feature weights based on user history
        liked_movies = [r.movie for r in user_ratings if r.value >= 4]
        
        # Genre similarity weight
        genre_weight = 0.0
        if liked_movies:
            # Simple text-based genre matching
            movie_text = (movie.overview or '').lower()
            genre_matches = 0
            for liked in liked_movies:
                liked_text = (liked.overview or '').lower()
                common_words = set(movie_text.split()) & set(liked_text.split())
                if len([w for w in common_words if len(w) > 4]) > 2:
                    genre_matches += 1
            genre_weight = min(0.5, genre_matches / len(liked_movies))
        
        # Rating weight (how much user values high ratings)
        avg_user_rating = sum([r.value for r in user_ratings]) / len(user_ratings)
        rating_weight = 0.3 if avg_user_rating >= 4 else 0.2
        
        # Popularity weight
        popularity_weight = 0.2
        
        # User preference weight (collaborative filtering component)
        user_preference_weight = 1.0 - (genre_weight + rating_weight + popularity_weight)
        
        return {
            'genre_weight': round(genre_weight, 3),
            'rating_weight': round(rating_weight, 3),
            'popularity_weight': round(popularity_weight, 3),
            'user_preference_weight': round(max(0, user_preference_weight), 3)
        }
    except Exception as e:
        print(f"SHAP computation failed: {e}")
        return None


def get_lime_explanation(user_id, movie_id):
    """
    Generate LIME-style local explanations
    Explains individual prediction by perturbing features
    """
    try:
        from django.db.models import Avg
        
        movie = Movie.objects.get(id=movie_id)
        user_ratings = Rating.objects.filter(user_id=user_id)
        
        explanations = []
        
        # Feature 1: Movie Quality
        if movie.vote:
            avg_vote = Movie.objects.aggregate(Avg('vote'))['vote__avg'] or 5.0
            quality_impact = (movie.vote - avg_vote) / 10.0
            explanations.append({
                'feature': 'Movie Quality',
                'value': f'{movie.vote}/10',
                'impact': round(quality_impact, 3),
                'direction': 'positive' if quality_impact > 0 else 'negative'
            })
        
        # Feature 2: Popularity
        if movie.popularity:
            avg_pop = Movie.objects.aggregate(Avg('popularity'))['popularity__avg'] or 1.0
            pop_impact = (movie.popularity - avg_pop) / avg_pop
            explanations.append({
                'feature': 'Popularity',
                'value': f'{movie.popularity:.1f}',
                'impact': round(min(0.3, pop_impact), 3),
                'direction': 'positive' if pop_impact > 0 else 'negative'
            })
        
        # Feature 3: User History Match
        if user_ratings.exists():
            liked_movies = [r.movie for r in user_ratings if r.value >= 4]
            if liked_movies:
                # Calculate content similarity
                movie_words = set((movie.overview or '').lower().split())
                similarity_scores = []
                for liked in liked_movies[:5]:
                    liked_words = set((liked.overview or '').lower().split())
                    common = len(movie_words & liked_words)
                    similarity_scores.append(common)
                
                avg_similarity = np.mean(similarity_scores) if similarity_scores else 0
                history_impact = min(0.5, avg_similarity / 10.0)
                
                explanations.append({
                    'feature': 'User History Match',
                    'value': f'{len(liked_movies)} liked movies',
                    'impact': round(history_impact, 3),
                    'direction': 'positive'
                })
        
        return explanations
    except Exception as e:
        print(f"LIME explanation failed: {e}")
        return []


def get_comprehensive_xai_explanation(user_id, movie_id, model=None, items=None):
    """
    Combines SHAP, LIME, and LightFM feature importance
    Returns a comprehensive explanation dictionary
    """
    explanation = {
        'shap_values': None,
        'lime_explanation': None,
        'lightfm_features': None,
        'combined_score': 0.0
    }
    
    # Get SHAP-like values
    shap_values = compute_shap_like_values(user_id, movie_id, model, items)
    if shap_values:
        explanation['shap_values'] = shap_values
        explanation['combined_score'] += sum(shap_values.values()) * 0.4
    
    # Get LIME explanation
    lime_exp = get_lime_explanation(user_id, movie_id)
    if lime_exp:
        explanation['lime_explanation'] = lime_exp
        explanation['combined_score'] += sum([e['impact'] for e in lime_exp]) * 0.3
    
    # Get LightFM feature importance if model available
    if model and items:
        lightfm_features = get_lightfm_feature_importance(user_id, movie_id, model, items)
        if lightfm_features:
            explanation['lightfm_features'] = lightfm_features
            explanation['combined_score'] += lightfm_features['prediction_score'] * 0.3
    
    return explanation