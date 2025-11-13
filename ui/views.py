# ui/views.py
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from core.models import UserOnboarding

@login_required  # <- bas yehi chahiye
def app(request):
    # Check if user has completed onboarding
    try:
        onboarding = request.user.onboarding
        if not onboarding.completed:
            return redirect('ui:onboarding')
    except UserOnboarding.DoesNotExist:
        # Create onboarding record for new user
        UserOnboarding.objects.create(user=request.user, completed=False)
        return redirect('ui:onboarding')
    
    return render(request, 'app.html', {'key_set': bool(settings.TMDB_API_KEY)})

@login_required
def onboarding(request):
    """Onboarding page for new users to set up preferences"""
    return render(request, 'onboarding.html', {'key_set': bool(settings.TMDB_API_KEY)})
