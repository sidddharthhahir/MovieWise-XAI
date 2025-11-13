from django.contrib import admin
from .models import Movie, Rating, UserOnboarding
admin.site.register([Movie, Rating, UserOnboarding])
