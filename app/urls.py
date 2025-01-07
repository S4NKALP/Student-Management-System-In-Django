from django.urls import path
from app import views

urlpatterns = [
    path("dashboard", views.dashboard, name="dashboard"),
    path("studentdashboard", views.studentdashboard, name="studentdashboard"),
]
