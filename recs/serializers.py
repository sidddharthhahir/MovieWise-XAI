from rest_framework import serializers
from core.models import Movie, Rating
class MovieSer(serializers.ModelSerializer):
    class Meta:
        model=Movie
        fields=('id','title','overview','year','poster','vote','popularity')
class RatingSer(serializers.ModelSerializer):
    class Meta:
        model=Rating
        fields=('id','movie','value','created_at')
