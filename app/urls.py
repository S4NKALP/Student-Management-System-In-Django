from django.urls import path
from app import views

urlpatterns = [
    path("dashboard", views.dashboard, name="dashboard"),
    path("studentdashboard", views.studentdashboard, name="studentdashboard"),
    # path("marksheet", views.marksheet, name="marksheet"),
    path('marksheet/<int:pk>/', views.view_marksheet, name='app_marksheet_view')
    # path("course/manage", views.Add_Course, name="add_course"),
    # path("course/edit/<int:id>", views.Edit_Course, name="edit_course"),
    # path("course/delete/<int:id>", views.Delete_Course, name="delete_course"),
]
