"""
URL configuration for student_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from app.admin import custom_admin_site
from django.views.generic import RedirectView
from app import views
from app import auth

# Serve media files without requiring authentication
urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add other URL patterns
urlpatterns += [
    path("app/", include("app.urls")),
    path("admin/", custom_admin_site.urls),  # Admin site at /admin/
    path("", RedirectView.as_view(url="/app/dashboard/", permanent=False)),  # Redirect root to dashboard
    
    # Custom login and logout views
    path('login/', auth_views.LoginView.as_view(template_name='login/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    
    # Password reset views - main entry point
    path('password-reset/', auth.reset_password_options, name='password_reset'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
