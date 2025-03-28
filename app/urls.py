from django.urls import path
from . import views
from django.contrib import admin
from . import auth
from . import staffviews

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("student-dashboard/", views.studentDashboard, name="studentDashboard"),
    path("teacher-dashboard/", views.teacherDashboard, name="teacherDashboard"),
    path("request-leave/", views.request_leave, name="request_leave"),
    path("request-staff-leave/", views.request_staff_leave, name="request_staff_leave"),
    path("submit-feedback/", views.submit_feedback, name="submit_feedback"),
    path(
        "submit-institute-feedback/",
        views.submit_institute_feedback,
        name="submit_institute_feedback",
    ),
    path(
        "submit-staff-institute-feedback/",
        views.submit_staff_institute_feedback,
        name="submit_staff_institute_feedback",
    ),
    path("save-fcm-token/", views.saveFCMToken, name="saveFCMToken"),
    path("firebase-messaging-sw.js", views.showFirebaseJS, name="showFirebaseJS"),
    path("update-profile/", views.update_profile, name="update_profile"),
    path("change-password/", views.change_password, name="change_password"),
    path(
        "subject/<int:subject_id>/files/",
        views.get_subject_files,
        name="get_subject_files",
    ),
    path("get-subjects/", views.get_subjects, name="get_subjects"),
    path('get-teachers/', views.get_teachers, name='get_teachers'),
    path('get-course-duration/', views.get_course_duration, name='get_course_duration'),
    path('save-attendance/', views.save_attendance, name='save_attendance'),
    path('get-subject-schedule/', views.get_subject_schedule, name='get_subject_schedule'),
    path('get-attendance-form/', staffviews.get_attendance_form, name='get_attendance_form'),
    path('teacher-update-profile-picture/', views.teacher_update_profile_picture, name='teacher_update_profile_picture'),
    path('teacher-change-password/', views.teacher_change_password, name='teacher_change_password'),
    path('approve-student-leave/<int:leave_id>/', views.approve_student_leave, name='approve_student_leave'),
    path('reject-student-leave/<int:leave_id>/', views.reject_student_leave, name='reject_student_leave'),
    path('approve-staff-leave/<int:leave_id>/', views.approve_staff_leave, name='approve_staff_leave'),
    path('reject-staff-leave/<int:leave_id>/', views.reject_staff_leave, name='reject_staff_leave'),
    path('add-notice/', views.add_notice, name='add_notice'),
    path('delete-notice/<int:notice_id>/', views.delete_notice, name='delete_notice'),
    
    # Password reset paths
    path('password-reset/', auth.reset_password_options, name='reset_password_options'),
    path('password-reset/phone/', auth.password_reset_phone, name='phone_reset_password'),
    path('password-reset/phone/verify/', auth.password_reset_phone_verify, name='verify_reset_otp'),
    path('password-reset/phone/resend/', auth.resend_phone_otp, name='resend_phone_otp'),
    path('password-reset/email/', auth.password_reset_email, name='email_reset_password'),
    path('password-reset/email/verify/', auth.password_reset_email_verify, name='password_reset_done'),
    path('password-reset/email/resend/', auth.resend_email_code, name='resend_reset_code'),
    path('password-reset/set/', auth.set_new_password, name='set_new_password'),
    path('get-students/', staffviews.get_students, name='get_students'),
]

