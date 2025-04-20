from django.urls import path
from app import views
from app import auth
from app import staffviews
from app import studentviews
from app import parentviews
from app import admissionviews
from app import hodviews


# URL patterns for the main application
urlpatterns = [
    
    # Dashboard URLs ---------------------------------------------------
    path("dashboard/", views.dashboard, name="dashboard"),
    path("student-dashboard/", studentviews.studentDashboard, name="studentDashboard"),
    path("teacher-dashboard/", staffviews.teacherDashboard, name="teacherDashboard"),
    path("parent-dashboard/", parentviews.parent_dashboard, name="parentDashboard"),
    path(
        "admission-officer-dashboard/",
        admissionviews.admission_officer_dashboard,
        name="admissionOfficerDashboard",
    ),
    path("hodDashboard/", hodviews.hod_dashboard, name="hodDashboard"),
    
    # Notice Management ------------------------------------------------
    path("add-notice/", views.add_notice, name="add_notice"),
    path("delete-notice/<int:notice_id>/", views.delete_notice, name="delete_notice"),
    
    # Leave Management -------------------------------------------------
    # Student Leave
    path("request-leave/", views.request_leave, name="request_leave"),
    path(
        "approve-student-leave/<int:leave_id>/",
        views.approve_student_leave,
        name="approve_student_leave",
    ),
    path(
        "reject-student-leave/<int:leave_id>/",
        views.reject_student_leave,
        name="reject_student_leave",
    ),
    path("get-student-leaves/", views.get_student_leaves, name="get_student_leaves"),
    
    # Staff Leave
    path("request-staff-leave/", views.request_staff_leave, name="request_staff_leave"),
    path(
        "approve-staff-leave/<int:leave_id>/",
        views.approve_staff_leave,
        name="approve_staff_leave",
    ),
    path(
        "reject-staff-leave/<int:leave_id>/",
        views.reject_staff_leave,
        name="reject_staff_leave",
    ),
    path("get-staff-leaves/", views.get_staff_leaves, name="get_staff_leaves"),
    
    # Feedback --------------------------------------------------------
    # Student Feedback
    path("submit-feedback/", views.submit_feedback, name="submit_feedback"),
    path(
        "submit-institute-feedback/",
        views.submit_institute_feedback,
        name="submit_institute_feedback",
    ),
    
    # Staff Feedback
    path(
        "submit-staff-institute-feedback/",
        views.submit_staff_institute_feedback,
        name="submit_staff_institute_feedback",
    ),
    
    # Parent Feedback
    path(
        "parent/feedback/submit/",
        parentviews.submit_parent_feedback,
        name="submit_parent_feedback",
    ),
    path(
        "parent/feedback/institute/submit/",
        parentviews.submit_parent_institute_feedback,
        name="submit_parent_institute_feedback",
    ),
    
    # Profile Management ----------------------------------------------
    path("update-profile/", views.update_profile, name="update_profile"),
    path("change-password/", views.change_password, name="change_password"),
    path(
        "teacher-update-profile-picture/",
        views.teacher_update_profile_picture,
        name="teacher_update_profile_picture",
    ),
    path(
        "teacher-change-password/",
        views.teacher_change_password,
        name="teacher_change_password",
    ),
    
    # Subject and Course Management -----------------------------------
    path("add-subject/", hodviews.add_subject, name="add_subject"),
    path(
        "subject/<int:subject_id>/files/",
        views.get_subject_files,
        name="get_subject_files",
    ),
    path(
        "subject/<int:subject_id>/syllabus/",
        staffviews.view_subject_syllabus,
        name="view_subject_syllabus",
    ),
    path("get-subjects/", views.get_subjects, name="get_subjects"),
    path("get-teachers/", views.get_teachers, name="get_teachers"),
    path("get-course-duration/", views.get_course_duration, name="get_course_duration"),
    path(
        "get-subject-schedule/", views.get_subject_schedule, name="get_subject_schedule"
    ),
    path('subject/<int:subject_id>/view/', hodviews.view_subject, name='view_subject'),
    path('edit-subject/<int:subject_id>/', hodviews.edit_subject, name='edit_subject'),
    path('delete-subject/<int:subject_id>/', hodviews.delete_subject, name='delete_subject'),
    
    # Student Management
    path('add-student/', hodviews.add_student, name='add_student'),
    path('get-student/<int:student_id>/', hodviews.get_student, name='get_student'),
    path('edit-student/<int:student_id>/', hodviews.edit_student, name='edit_student'),
    path('delete-student/<int:student_id>/', hodviews.delete_student, name='delete_student'),
    
    # HOD Notice Management
    path('hod/add-notice/', hodviews.add_notice, name='hod_add_notice'),
    path('notice/<int:notice_id>/', hodviews.view_notice, name='view_notice'),
    path('delete-notice/<int:notice_id>/', hodviews.delete_notice, name='delete_notice'),
    
    # Subject File Management
    path(
        "delete-subject-file/",
        staffviews.delete_subject_file,
        name="delete_subject_file",
    ),
    path(
        "get-teacher-subjects/",
        staffviews.get_teacher_subjects,
        name="get_teacher_subjects",
    ),
    
    # Attendance Management -------------------------------------------
    path("save-attendance/", views.save_attendance, name="save_attendance"),
    path(
        "get-attendance-form/",
        staffviews.get_attendance_form,
        name="get_attendance_form",
    ),
    
    # Password Management ---------------------------------------------
    # Password Reset Options
    path("password-reset/", auth.reset_password_options, name="reset_password_options"),
    
    # Phone-based Reset
    path(
        "password-reset/phone/", auth.password_reset_phone, name="phone_reset_password"
    ),
    path(
        "password-reset/phone/verify/",
        auth.password_reset_phone_verify,
        name="verify_reset_otp",
    ),
    path(
        "password-reset/phone/resend/", auth.resend_phone_otp, name="resend_phone_otp"
    ),
    
    # Email-based Reset
    path(
        "password-reset/email/", auth.password_reset_email, name="email_reset_password"
    ),
    path(
        "password-reset/email/verify/",
        auth.password_reset_email_verify,
        name="password_reset_done",
    ),
    path(
        "password-reset/email/resend/", auth.resend_email_code, name="resend_reset_code"
    ),
    
    # New Password Setup
    path("password-reset/set/", auth.set_new_password, name="set_new_password"),
    
    # Password Security
    path("check-weak-password/", views.check_weak_password, name="check_weak_password"),
    
    # Parent-Teacher Meeting ------------------------------------------
    path("parent/meetings/", parentviews.parent_meetings, name="parent_meetings"),
    path("api/meetings/add/", parentviews.add_meeting, name="add_meeting"),
    path(
        "api/meetings/<int:meeting_id>/complete/",
        parentviews.complete_meeting,
        name="complete_meeting",
    ),
    path(
        "api/meetings/<int:meeting_id>/cancel/",
        parentviews.cancel_meeting,
        name="cancel_meeting",
    ),
    path(
        "api/meetings/<int:meeting_id>/reschedule/",
        parentviews.reschedule_meeting,
        name="reschedule_meeting",
    ),
    path(
        "api/meetings/<int:meeting_id>/notes/",
        parentviews.get_meeting_notes,
        name="get_meeting_notes",
    ),
    path(
        "api/meetings/<int:meeting_id>/agenda/",
        parentviews.get_meeting_agenda,
        name="get_meeting_agenda",
    ),
    path(
        "api/meetings/<int:meeting_id>/cancellation-reason/",
        views.get_meeting_cancellation_reason,
        name="get_meeting_cancellation_reason",
    ),
    
    # API Endpoints --------------------------------------------------
    # Student API
    path(
        "api/students/<int:student_id>/details/",
        parentviews.get_student_details,
        name="get_student_details",
    ),
    path("get-students/", staffviews.get_students, name="get_students"),
    
    # Meeting API Endpoints (HOD)
    path("api/hod/meetings/<int:meeting_id>/", hodviews.api_get_meeting, name="api_get_meeting"),
    path("api/hod/meetings/", hodviews.api_create_meeting, name="api_create_meeting"),
    path("api/hod/meetings/<int:meeting_id>/edit/", hodviews.api_update_meeting, name="api_update_meeting"),
    path("api/hod/meetings/<int:meeting_id>/cancel/", hodviews.api_cancel_meeting, name="api_cancel_meeting"),
    path("api/hod/meetings/<int:meeting_id>/notes/", hodviews.get_meeting_notes, name="get_meeting_notes"),
    path("api/hod/meetings/<int:meeting_id>/agenda/", hodviews.get_meeting_agenda, name="get_meeting_agenda"),
    path("api/hod/meetings/<int:meeting_id>/cancellation-reason/", hodviews.get_cancellation_reason, name="get_cancellation_reason"),
    
    # Routine API Endpoints (HOD)
    path("api/hod/routines/", hodviews.api_create_routine, name="api_create_routine"),
    path("api/hod/routines/<int:routine_id>/", hodviews.api_get_routine, name="api_get_routine"),
    path("api/hod/routines/<int:routine_id>/edit/", hodviews.api_update_routine, name="api_update_routine"),
    path("api/hod/routines/<int:routine_id>/delete/", hodviews.api_delete_routine, name="api_delete_routine"),
    
    # Progress API Endpoints (HOD)
    path("api/get-student-progress/", hodviews.get_student_progress, name="get_student_progress"),
    path("api/get-progress/<int:progress_id>/", hodviews.get_progress, name="get_progress"),
    path("api/edit-progress/<int:progress_id>/", hodviews.edit_progress, name="edit_progress"),
    
    # Firebase Cloud Messaging ---------------------------------------
    path("saveFCMToken/", views.save_fcm_token, name="saveFCMToken"),

    # Admission Officer routes ----------------------------------------
    path("add-student/", admissionviews.add_student, name="add_student"),
    path("add-batch/", admissionviews.add_batch, name="add_batch"),
    path("add-course/", admissionviews.add_course, name="add_course"),
    path(
        "add-course-tracking/",
        admissionviews.add_course_tracking,
        name="add_course_tracking",
    ),
    path("get-courses/", admissionviews.get_courses, name="get_courses"),
    path("get-batches/", admissionviews.get_batches, name="get_batches"),
    path(
        "admission-get-students/",
        admissionviews.get_students,
        name="admission_get_students",
    ),
    path(
        "get-student/<int:student_id>/", admissionviews.get_student, name="get_student"
    ),
    path("edit-student/", admissionviews.edit_student, name="edit_student"),
    path(
        "get-course-tracking/<int:tracking_id>/",
        admissionviews.get_course_tracking,
        name="get_course_tracking",
    ),
    path(
        "edit-course-tracking/",
        admissionviews.edit_course_tracking,
        name="edit_course_tracking",
    ),

    # Staff Management URLs
    path('staff/<int:staff_id>/', hodviews.view_staff, name='view_staff'),
    path('edit-staff/<int:staff_id>/', hodviews.edit_staff, name='edit_staff'),
    path('delete-staff/<int:staff_id>/', hodviews.delete_staff, name='delete_staff'),
    path('add-staff/', hodviews.add_staff, name='add_staff'),

    # Test endpoints (commented out)
    # path('test/error/505/', views.test_505_error, name='test_505_error'),
]
