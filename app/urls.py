from django.urls import path
from app import adminViews

urlpatterns = [
    path("dashboard/", adminViews.admin_home, name="dashboard"),
    path("add_course/", adminViews.add_course, name="add_course"),
    path("manage_course", adminViews.manage_course, name="manage_course"),
    path("delete_course/<course_id>/", adminViews.delete_course, name="delete_course"),
    path("edit_course/<int:course_id>/", adminViews.edit_course, name="edit_course"),
    path("add_academicyear/", adminViews.add_academicyear, name="add_academicyear"),
    path(
        "manage_academicyear/",
        adminViews.manage_academicyear,
        name="manage_academicyear",
    ),
    path(
        "delete_academicyear/<academic_year_id>/",
        adminViews.delete_academicyear,
        name="delete_academicyear",
    ),
    path(
        "edit_academicyears/<int:pk>/",
        adminViews.edit_academicyear,
        name="edit_academicyear",
    ),
    path("manage_subject/", adminViews.manage_subjects, name="manage_subject"),
    path("add_subject/", adminViews.add_subject, name="add_subject"),
    path("edit_subject/<int:pk>/", adminViews.edit_subject, name="edit_subject"),
    path(
        "delete_subject/<subject_id>/", adminViews.delete_subject, name="delete_subject"
    ),
]

