from django.db import models
from django.contrib.auth.models import User
class Movie(models.Model):
    tmdb_id=models.IntegerField(unique=True, null=True, blank=True)
    title=models.CharField(max_length=255)
    overview=models.TextField(blank=True)
    year=models.CharField(max_length=4, blank=True)
    poster=models.URLField(blank=True)
    popularity=models.FloatField(default=0)
    vote=models.FloatField(default=0)
    def __str__(self): return self.title
    
class Rating(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    movie=models.ForeignKey(Movie, on_delete=models.CASCADE)
    value=models.IntegerField(default=5)
    created_at=models.DateTimeField(auto_now_add=True)

class UserOnboarding(models.Model):
    """Track onboarding completion for users"""
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='onboarding')
    completed=models.BooleanField(default=False)
    ratings_count=models.IntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    completed_at=models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Onboarding for {self.user.username}"
