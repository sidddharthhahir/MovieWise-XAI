from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from accounts.views import LogoutGetView


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('recs.api_urls')),
    path('api/rag/', include('rag.api_urls')),

    path('accounts/', include('accounts.urls')),  # your signup etc.

    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),

    # ✅ allow GET logout and redirect to home
    path('accounts/logout/', LogoutGetView.as_view(next_page='login'), name='logout'),

    path('', include(('ui.urls', 'ui'), namespace='ui')),
]
