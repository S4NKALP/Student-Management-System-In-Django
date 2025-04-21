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
from django.views.generic import RedirectView, TemplateView
from app import views
from app import auth

# Main URL patterns for the project
urlpatterns = [
    # Application URLs ------------------------------------------------
    path("app/", include("app.urls")),
    # path("", custom_admin_site.urls, name="admin"),
    # Root Redirect --------------------------------------------------
    # path("", RedirectView.as_view(url="/app/dashboard/", permanent=False)),
    # Authentication -------------------------------------------------
    path("login/", auth.custom_login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/login/"), name="logout"),
    # Password Management --------------------------------------------
    path("password-reset/", auth.reset_password_options, name="password_reset"),
    # Firebase Service -----------------------------------------------
    path("firebase-messaging-sw.js", views.serve_firebase_sw),
]

urlpatterns.append(path("", custom_admin_site.urls, name="admin"))
# Static and Media Files (Development Only) --------------------------
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error Handlers ----------------------------------------------------
handler400 = "app.error_handlers.handler400"
handler403 = "app.error_handlers.handler403"
handler404 = "app.error_handlers.handler404"
handler500 = "app.error_handlers.handler500"
handler505 = "app.error_handlers.handler505"
