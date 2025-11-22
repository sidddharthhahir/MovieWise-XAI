from django.urls import path
from .views import (
    tmdb_discover,
    rate_movie,
    recommendations,
    trending,
    explain_any,
    natural_explanation,
    complete_onboarding,
    get_user_ratings,
    counterfactual_explanation,
)

urlpatterns = [
    path('discover/', tmdb_discover),
    path('ratings/', rate_movie),
    path('recommendations/', recommendations),
    path('trending/', trending),
    path('explain/', explain_any),
    path('natural-explanation/', natural_explanation),
    path('onboarding/complete/', complete_onboarding),
    path('user-ratings/', get_user_ratings),
    path('counterfactual-explanation/', counterfactual_explanation, name='counterfactual_explanation'),
]