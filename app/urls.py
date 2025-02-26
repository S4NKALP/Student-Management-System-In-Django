from django.urls import path
from app import adminViews, studentViews, teacherViews

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
    path("manage_student/", adminViews.manage_student, name="manage_student"),
    path("add_student/", adminViews.add_student, name="add_student"),
    path(
        "edit_student/<int:student_id>/", adminViews.edit_student, name="edit_student"
    ),
    path(
        "delete_student/<int:student_id>/",
        adminViews.delete_student,
        name="delete_student",
    ),
    path("manage_teacher/", adminViews.manage_teacher, name="manage_teacher"),
    path("add_teacher/", adminViews.add_teacher, name="add_teacher"),
    path(
        "edit_teacher/<int:teacher_id>/", adminViews.edit_teacher, name="edit_teacher"
    ),
    path(
        "delete_teacher/<int:teacher_id>/",
        adminViews.delete_teacher,
        name="delete_teacher",
    ),
    path(
        "student_feedback_message/",
        adminViews.student_feedback_message,
        name="student_feedback_message",
    ),
    path(
        "student_feedback_message_reply/",
        adminViews.student_feedback_message_reply,
        name="student_feedback_message_reply",
    ),
    path(
        "teacher_feedback/",
        adminViews.teacher_feedback,
        name="teacher_feedback",
    ),
    path(
        "teacher_feedback_replied/",
        adminViews.teacher_feedback_replied,
        name="teacher_feedback_replied",
    ),
    path(
        "student_leave_view/", adminViews.student_leave_view, name="student_leave_view"
    ),
    path(
        "student_leave_approve/<leave_id>/",
        adminViews.student_leave_approve,
        name="student_leave_approve",
    ),
    path(
        "student_leave_reject/<leave_id>/",
        adminViews.student_leave_reject,
        name="student_leave_reject",
    ),
    path(
        "teacher_leave_view/", adminViews.teacher_leave_view, name="teacher_leave_view"
    ),
    path(
        "teacher_leave_approve/<leave_id>/",
        adminViews.teacher_leave_approve,
        name="teacher_leave_approve",
    ),
    path(
        "teacher_leave_reject/<leave_id>/",
        adminViews.teacher_leave_reject,
        name="teacher_leave_reject",
    ),
    path(
        "admin_view_attendance/",
        adminViews.admin_view_attendance,
        name="admin_view_attendance",
    ),
    path(
        "admin_get_attendance_dates/",
        adminViews.admin_get_attendance_dates,
        name="admin_get_attendance_dates",
    ),
    path(
        "admin_get_attendance_student/",
        adminViews.admin_get_attendance_student,
        name="admin_get_attendance_student",
    ),
    # ── Student ───────────────────────────────────────────────────────────
    path(
        "student_dashboard/", studentViews.student_dashboard, name="student_dashboard"
    ),
    # ── teacher ───────────────────────────────────────────────────────────
    path(
        "teacher_dashboard/", teacherViews.teacher_dashboard, name="teacher_dashboard"
    ),
]
