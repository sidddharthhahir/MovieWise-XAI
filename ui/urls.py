from django.urls import path
from .views import app, onboarding
urlpatterns=[path('', app, name='app'), path('onboarding/', onboarding, name='onboarding')]
