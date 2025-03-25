from django.urls import path
from app import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student-dashboard/', views.studentDashboard, name='studentDashboard'),
    path('teacher-dashboard/', views.teacherDashboard, name='teacherDashboard'),
] 