from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.models import Movie, Rating
from .serializers import MovieSer, RatingSer
from .tmdb import discover, search_person, get_genres, IMG, detail

LANG_ALIASES = {"hindi":"hi","hin":"hi","english":"en","eng":"en","urdu":"ur","turkish":"tr","spanish":"es","german":"de","french":"fr","japanese":"ja","korean":"ko","tamil":"ta","telugu":"te","marathi":"mr","kannada":"kn","bengali":"bn","gujarati":"gu","punjabi":"pa","malayalam":"ml"}

def _user_specific_explain(movie, user_id, max_popularity):
    """Generate highly user-specific explanations based on rating history"""
    from core.models import Rating
    
    # Get user's rating history
    user_ratings = Rating.objects.filter(user_id=user_id)
    
    # Start with always-true quality explanations
    explanations = []
    vote01 = (movie.vote or 0) / 10.0
    pop01 = (movie.popularity or 0) / (max_popularity or 1.0)
    
    # Add quality-based explanations
    if movie.vote and movie.vote >= 6.5:
        explanations.append({
            "feature": "Highly rated",
            "value": f"TMDB score: {movie.vote}/10",
            "weight": 0.3,
            "contribution": round(0.3 * vote01, 3)
        })
    
    if movie.popularity and movie.popularity > max_popularity * 0.3:
        explanations.append({
            "feature": "Popular choice",
            "value": f"Popularity: {movie.popularity:.1f}",
            "weight": 0.2,
            "contribution": round(0.2 * pop01, 3)
        })
    
    # Add highly user-specific explanations if we have rating history
    if user_ratings.exists():
        # Find movies the user liked (rating >= 4)
        liked_movies = [r.movie for r in user_ratings if r.value >= 4]
        
        if liked_movies:
            # Check for title/overview similarity
            movie_text = f"{movie.title} {movie.overview or ''}".lower()
            similar_count = 0
            
            for liked_movie in liked_movies:
                liked_text = f"{liked_movie.title} {liked_movie.overview or ''}".lower()
                # Check for common meaningful words (length > 3)
                common_words = set(movie_text.split()) & set(liked_text.split())
                significant_words = [word for word in common_words if len(word) > 3]
                if significant_words:
                    similar_count += 1
            
            # If we found similarities, highlight them
            if similar_count > 0:
                explanations.append({
                    "feature": f"Based on your likes",
                    "value": f"Similar to {similar_count} movie{'s' if similar_count > 1 else ''} you rated highly",
                    "weight": 0.4,
                    "contribution": 0.4
                })
            else:
                # Look for genre/theme matching
                genre_keywords = {
                    'action': ['action', 'fight', 'battle', 'war', 'combat', 'violence'],
                    'comedy': ['funny', 'humor', 'comedy', 'laugh', 'comic', 'hilarious'],
                    'drama': ['drama', 'emotional', 'family', 'relationship', 'life', 'drama'],
                    'thriller': ['suspense', 'mystery', 'crime', 'detective', 'killer', 'threat'],
                    'romance': ['romance', 'love', 'romantic', 'heart', 'wedding', 'couple'],
                    'horror': ['horror', 'scary', 'frightening', 'monster', 'ghost', 'death']
                }
                
                movie_genres = []
                for genre, keywords in genre_keywords.items():
                    if any(keyword in movie_text for keyword in keywords):
                        movie_genres.append(genre)
                
                if movie_genres:
                    # Count how many liked movies match this genre
                    matching_likes = 0
                    for liked_movie in liked_movies:
                        liked_text_lower = f"{liked_movie.title} {liked_movie.overview or ''}".lower()
                        if any(keyword in liked_text_lower for keyword in genre_keywords[movie_genres[0]]):
                            matching_likes += 1
                    
                    explanations.append({
                        "feature": f"Your {movie_genres[0]} taste",
                        "value": f"You've rated {matching_likes} {movie_genres[0]} movies highly",
                        "weight": 0.4,
                        "contribution": 0.4
                    })
                else:
                    # General taste analysis
                    avg_user_rating = sum([r.value for r in user_ratings]) / len(user_ratings)
                    explanations.append({
                        "feature": "Matches your taste",
                        "value": f"Similar to movies you rated {avg_user_rating:.1f}/5",
                        "weight": 0.4,
                        "contribution": 0.4
                    })
        
        # Add detailed rating history insights
        total_ratings = user_ratings.count()
        high_ratings = user_ratings.filter(value__gte=4).count()
        low_ratings = user_ratings.filter(value__lte=2).count()
        
        if total_ratings > 0:
            explanations.append({
                "feature": f"Your movie profile",
                "value": f"You rate movies {high_ratings} high, {low_ratings} low out of {total_ratings}",
                "weight": 0.1,
                "contribution": 0.1
            })
    
    # Ensure we have comprehensive explanations
    if len(explanations) < 2:
        if user_ratings.exists():
            explanations.append({
                "feature": "Personalized match",
                "value": "Based on your viewing patterns",
                "weight": 0.3,
                "contribution": 0.3
            })
        else:
            explanations.append({
                "feature": "Quality choice",
                "value": "Highly rated by similar users",
                "weight": 0.3,
                "contribution": 0.3
            })
    
    # Calculate overall score
    score = sum([exp["contribution"] for exp in explanations])
    
    return score, explanations

def _simple_explain(vote, popularity, max_popularity):
    vote01=(vote or 0)/10.0; pop01=(popularity or 0)/(max_popularity or 1.0)
    score=0.6*vote01 + 0.4*pop01
    return score,[{"feature":"TMDB rating","value":vote,"weight":0.6,"contribution":round(0.6*vote01,3)},{"feature":"Popularity","value":popularity,"weight":0.4,"contribution":round(0.4*pop01,3)}]

@api_view(['GET'])
@permission_classes([AllowAny])
def tmdb_discover(request):
    actor=(request.GET.get('actor') or '').strip()
    genre=(request.GET.get('genre') or '').strip()
    lang=(request.GET.get('lang') or '').strip().lower()

    person_id=None
    if actor:
        res=search_person(actor); person_id=res[0]['id'] if res else None

    gmap={g['name'].lower(): g['id'] for g in get_genres()}
    gid=gmap.get(genre.lower()) if genre else None

    if lang and len(lang)>2: lang=LANG_ALIASES.get(lang,'')

    params={}
    if person_id: params['with_cast']=person_id
    if gid: params['with_genres']=gid
    if lang: params['with_original_language']=lang

    items=discover(**params) if params else discover()
    maxp=max([i.get('popularity') or 0 for i in items] or [1.0])
    out=[]
    for i in items[:20]:
        vote=i.get('vote_average'); pop=i.get('popularity')
        score,reasons=_simple_explain(vote,pop,maxp)
        out.append({"tmdb_id":i.get("id"),"title":i.get("title"),"overview":i.get("overview"),"poster":(IMG+i["poster_path"]) if i.get("poster_path") else None,"vote":vote,"year":(i.get("release_date") or "")[:4],"popularity":pop,"xai":{"score":round(score,3),"reasons":reasons}})
    return Response({"results":out})

@api_view(['GET'])
@permission_classes([AllowAny])
def explain_any(request):
    movie_id=request.GET.get('movie_id'); tmdb_id=request.GET.get('tmdb_id')
    user_id=request.user.id if request.user.is_authenticated else 1
    
    if movie_id:
        try: m=Movie.objects.get(id=int(movie_id))
        except Movie.DoesNotExist: return Response({"error":"movie not found"}, status=404)
        from django.db.models import Max
        maxp=Movie.objects.aggregate(Max('popularity'))['popularity__max'] or 1.0
        score,reasons=_user_specific_explain(m, user_id, maxp)
        return Response({"movie":m.title,"score":round(score,3),"reasons":reasons})
    if tmdb_id:
        d=detail(int(tmdb_id)); vote=d.get('vote_average') or 0.0; pop=d.get('popularity') or 0.0
        score,reasons=_simple_explain(vote,pop,max(1.0,pop))
        return Response({"movie":d.get('title'),"score":round(score,3),"reasons":reasons})
    return Response({"error":"provide movie_id or tmdb_id"}, status=400)

@api_view(['POST'])
def rate_movie(request):
    user=request.user if request.user.is_authenticated else None
    movie_data=request.data.get('movie')  # Can be either local movie ID or TMDB ID
    value=int(request.data.get('value',5))
    
    # Handle TMDB ID (for onboarding) or local movie ID
    if isinstance(movie_data, str) and movie_data.isdigit():
        # This is likely a TMDB ID from onboarding
        tmdb_id = int(movie_data)
        
        # Check if movie already exists in our database
        try:
            movie = Movie.objects.get(tmdb_id=tmdb_id)
        except Movie.DoesNotExist:
            # Get movie details from TMDB and create the movie
            try:
                movie_detail = detail(tmdb_id)
                movie = Movie.objects.create(
                    tmdb_id=tmdb_id,
                    title=movie_detail.get('title', ''),
                    overview=movie_detail.get('overview', ''),
                    year=(movie_detail.get('release_date') or '')[:4],
                    poster=(IMG + movie_detail['poster_path']) if movie_detail.get('poster_path') else '',
                    popularity=movie_detail.get('popularity', 0.0),
                    vote=movie_detail.get('vote_average', 0.0)
                )
            except Exception as e:
                return Response({"error": f"Failed to fetch movie details: {str(e)}"}, status=400)
        
        movie_id = movie.id
    else:
        # This is a local movie ID
        movie_id = int(movie_data)
    
    r=Rating.objects.create(user=user, movie_id=movie_id, value=value)
    return Response(RatingSer(r).data)

@api_view(['GET'])
def natural_explanation(request):
    """
    Generate natural language explanations using:
    1. SHAP/LIME from LightFM model
    2. RAG for context retrieval
    3. LLM for natural language generation
    """
    movie_id = request.GET.get('movie_id')
    tmdb_id = request.GET.get('tmdb_id')
    user_id = request.user.id if request.user.is_authenticated else 1
    
    # Get movie information
    if movie_id:
        try:
            movie = Movie.objects.get(id=int(movie_id))
        except Movie.DoesNotExist:
            return Response({"error": "Movie not found"}, status=404)
    elif tmdb_id:
        try:
            movie_detail = detail(int(tmdb_id))
            movie = Movie(
                title=movie_detail.get('title', ''),
                overview=movie_detail.get('overview', ''),
                vote=movie_detail.get('vote_average', 0.0),
                popularity=movie_detail.get('popularity', 0.0)
            )
        except Exception as e:
            return Response({"error": f"Failed to fetch movie: {str(e)}"}, status=400)
    else:
        return Response({"error": "Provide movie_id or tmdb_id"}, status=400)
    
    # ===== STEP 1: Get XAI Explanations (SHAP + LIME + LightFM) =====
    from .xai_explainer import get_comprehensive_xai_explanation
    from .lightfm_pipeline import load_artifacts
    
    xai_explanation = None
    try:
        artifacts = load_artifacts()
        model = artifacts.get('model') if artifacts.get('mode') == 'lightfm' else None
        items = artifacts.get('items', [])
        
        xai_explanation = get_comprehensive_xai_explanation(
            user_id=user_id,
            movie_id=movie.id if movie_id else None,
            model=model,
            items=items
        )
    except Exception as e:
        print(f"XAI explanation failed: {e}")
    
    # ===== STEP 2: Get RAG Context =====
    rag_context = ""
    similar_movies = []
    try:
        from rag.embeddings import store
        query = f"{movie.title} {movie.overview or ''}"
        hits = store.search(query, k=3)
        
        if hits:
            movie_ids = [i for i, _ in hits]
            similar_movies_objs = Movie.objects.filter(id__in=movie_ids)
            similar_movies = [
                f"{m.title} ({m.vote}/10)" for m in similar_movies_objs
            ]
            rag_context = f"Similar movies: {', '.join(similar_movies)}. "
    except Exception as e:
        print(f"RAG retrieval failed: {e}")
    
    # ===== STEP 3: Build User Context =====
    from core.models import Rating
    user_ratings = Rating.objects.filter(user_id=user_id)
    
    user_context = ""
    if user_ratings.exists():
        liked_movies = [r for r in user_ratings if r.value >= 4]
        if liked_movies:
            liked_titles = [f"{r.movie.title} ({r.value}/5)" for r in liked_movies[:3]]
            user_context = f"User liked: {', '.join(liked_titles)}. "
    else:
        user_context = "New user with no rating history. "
    
    # ===== STEP 4: Build Enhanced LLM Prompt with XAI + RAG =====
    prompt_parts = [
        f"Movie: '{movie.title}' (Rating: {movie.vote}/10, Popularity: {movie.popularity}).",
        f"Overview: {movie.overview[:200] if movie.overview else 'N/A'}.",
        user_context,
        rag_context
    ]
    
    # Add SHAP values to prompt
    if xai_explanation and xai_explanation.get('shap_values'):
        shap = xai_explanation['shap_values']
        prompt_parts.append(
            f"Feature importance: Genre ({shap['genre_weight']}), "
            f"Rating ({shap['rating_weight']}), "
            f"Popularity ({shap['popularity_weight']}), "
            f"User preference ({shap['user_preference_weight']})."
        )
    
    # Add LIME explanation to prompt
    if xai_explanation and xai_explanation.get('lime_explanation'):
        lime_features = [f"{e['feature']} ({e['impact']})" for e in xai_explanation['lime_explanation'][:2]]
        prompt_parts.append(f"Key factors: {', '.join(lime_features)}.")
    
    full_prompt = " ".join(prompt_parts)
    full_prompt += " Explain in 40 words why this movie is recommended."
    
    # ===== STEP 5: Generate LLM Explanation =====
    try:
        from core.services import openrouter_service
        print("🔍 Calling LLM with XAI + RAG prompt...")
        explanation = openrouter_service.generate_explanation(user_context, full_prompt)
        print("✅ LLM returned:", (explanation[:120] + '...') if isinstance(explanation, str) else explanation)
        
        if explanation:
            return Response({
                "movie": movie.title,
                "explanation": explanation,
                "type": "llm_with_xai_and_rag",
                "xai_details": xai_explanation,
                "similar_movies": similar_movies,
                "shap_values": xai_explanation.get('shap_values') if xai_explanation else None,
                "lime_explanation": xai_explanation.get('lime_explanation') if xai_explanation else None
            })
        else:
            print("⚠️ LLM returned empty explanation, falling back to RAG")
    except Exception as e:
        print(f"❌ LLM generation failed: {e}")
    
    # ===== STEP 6: Fallback to RAG-only explanation =====
    if rag_context:
        rag_explanation = f"This movie is similar to {similar_movies[0] if similar_movies else 'highly rated films'}. "
        if xai_explanation and xai_explanation.get('shap_values'):
            shap = xai_explanation['shap_values']
            top_feature = max(shap, key=shap.get)
            rag_explanation += f"Recommended primarily based on {top_feature.replace('_', ' ')}."
        
        return Response({
            "movie": movie.title,
            "explanation": rag_explanation,
            "type": "rag_with_xai_fallback",
            "xai_details": xai_explanation,
            "similar_movies": similar_movies
        })
    
    # ===== STEP 7: Final Simple Fallback =====
    from django.db.models import Max
    maxp = Movie.objects.aggregate(Max('popularity'))['popularity__max'] or 1.0
    score, reasons = _simple_explain(movie.vote, movie.popularity, maxp)
    
    simple_explanation = f"Rated {movie.vote or 'N/A'}/10 with popularity {movie.popularity or 'N/A'}."
    if xai_explanation and xai_explanation.get('combined_score'):
        simple_explanation += f" XAI confidence score: {xai_explanation['combined_score']:.2f}."
    
    return Response({
        "movie": movie.title,
        "explanation": simple_explanation,
        "type": "simple_with_xai_fallback",
        "xai_details": xai_explanation
    })

@api_view(['GET'])
def recommendations(request):
    from .lightfm_pipeline import topn_for_user
    from core.models import Rating
    user_id=request.user.id if request.user.is_authenticated else 1
    k=int(request.GET.get('k',12))
    
    # Check if user has at least 5 ratings for meaningful personalization
    user_ratings = Rating.objects.filter(user_id=user_id)
    rating_count = user_ratings.count()
    
    if rating_count < 5:
        return Response({
            "error": "insufficient_ratings",
            "message": f"Please rate {5 - rating_count} more movie(s) to get personalized recommendations.",
            "current_ratings": rating_count,
            "required_ratings": 5,
            "action": "rate_more_movies"
        })
    
    recs=topn_for_user(user_id=user_id, k=k)
    return Response(MovieSer(recs, many=True).data)

@api_view(['GET'])
def trending(request):
    from .tmdb import get_tmdb_trending
    from .serializers import MovieSer
    k=int(request.GET.get('k',12))
    time_window = request.GET.get('time_window', 'week') # 'day' or 'week'

    try:
        # Fetch trending movies directly from TMDB
        trending_results = get_tmdb_trending(time_window=time_window)
        # We only need basic movie info for the card display
        # No need to store them in our DB just for trending display
        out = []
        for i in trending_results[:k]:
            out.append({
                "tmdb_id": i.get("id"),
                "title": i.get("title"),
                "overview": i.get("overview"),
                "poster": (IMG + i["poster_path"]) if i.get("poster_path") else None,
                "vote": i.get("vote_average"),
                "year": (i.get("release_date") or "")[:4],
                "popularity": i.get("popularity"),
            })
        return Response(out)
    except Exception as e:
        return Response({"error": f"Failed to fetch trending movies from TMDB: {str(e)}"}, status=500)

@api_view(['POST'])
def complete_onboarding(request):
    """Complete the onboarding process for the current user"""
    from core.models import UserOnboarding, Rating
    from django.utils import timezone
    user = request.user
    
    try:
        onboarding = user.onboarding
        rating_count = Rating.objects.filter(user=user).count()
        
        # Update onboarding record
        onboarding.completed = True
        onboarding.ratings_count = rating_count
        onboarding.completed_at = timezone.now()
        onboarding.save()
        
        return Response({"status": "success", "message": "Onboarding completed successfully"})
    except UserOnboarding.DoesNotExist:
        return Response({"error": "Onboarding record not found"}, status=404)
    except Exception as e:
        return Response({"error": f"Failed to complete onboarding: {str(e)}"}, status=500)


@api_view(['GET'])
def get_user_ratings(request):
    """Get user's ratings for a list of movies (by movie_id or tmdb_id)"""
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)

    movie_ids = request.GET.getlist('movie_id')  # List of local movie IDs
    tmdb_ids = request.GET.getlist('tmdb_id')    # List of TMDB IDs

    ratings_map = {} # Maps movie.id to rating value

    if movie_ids:
        ratings = Rating.objects.filter(user=user, movie_id__in=movie_ids).select_related('movie')
        for r in ratings:
            ratings_map[r.movie.id] = r.value
    
    if tmdb_ids:
        # Get movies from our DB that match the tmdb_ids
        movies_in_db = Movie.objects.filter(tmdb_id__in=tmdb_ids)
        local_movie_ids_from_tmdb = [m.id for m in movies_in_db]

        if local_movie_ids_from_tmdb:
            ratings = Rating.objects.filter(user=user, movie_id__in=local_movie_ids_from_tmdb).select_related('movie')
            for r in ratings:
                ratings_map[r.movie.tmdb_id] = r.value # Map by tmdb_id for frontend matching

    return Response(ratings_map)
