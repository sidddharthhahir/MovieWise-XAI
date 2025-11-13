from django.urls import path
from .views import tmdb_discover, rate_movie, recommendations, trending, explain_any, complete_onboarding, natural_explanation, get_user_ratings
urlpatterns=[path('discover/', tmdb_discover), path('ratings/', rate_movie), path('recommendations/', recommendations), path('trending/', trending), path('explain/', explain_any), path('natural-explanation/', natural_explanation), path('onboarding/complete/', complete_onboarding), path('user-ratings/', get_user_ratings)]
