from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from app.models import (
    Student,
    Teacher,
    AcademicYear,
    Course,
    Subject,
    Attendance,
    AttendanceReport,
    LeaveReportStudent,
    LeaveReportTeacher,
    FeedbackStudent,
    FeedbackTeacher,
)
# Register your models here.

admin.site.register(FeedbackStudent)
admin.site.register(FeedbackTeacher)
admin.site.register(LeaveReportStudent)
admin.site.register(LeaveReportTeacher)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("id", "start_date", "created_at", "updated_at")

    def changelist_view(self, request, extra_context=None):
        return redirect(reverse("manage_academicyear"))


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("subject_id", "attendance_date", "created_at", "updated_at")


@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    list_display = ("student_id", "attendance_id", "status", "created_at", "updated_at")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "middle_name",
        "last_name",
        "username",
        "email",
        "phone",
        "dob",
        "gender",
        "address",
        "father_name",
        "mother_name",
        "parents_number",
        "father_occupation",
        "guardian_name",
        "relationship_with_student",
    )
    search_fields = (
        "first_name",
        "middle_name",
        "last_name",
        "email",
        "phone",
        "father_name",
        "mother_name",
        "guardian_name",
    )
    list_filter = (
        "gender",
        "father_occupation",
        "mother_occupation",
        "relationship_with_student",
    )
    list_editable = ("phone", "email", "gender", "address")
    date_hierarchy = "dob"
    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "dob",
                    "gender",
                    "address",
                )
            },
        ),
        ("Contact Information", {"fields": ("username", "password", "phone", "email")}),
        (
            "Parent Details",
            {
                "fields": (
                    "father_name",
                    "mother_name",
                    "parents_number",
                    "father_occupation",
                    "mother_occupation",
                )
            },
        ),
        (
            "Guardian Details",
            {
                "fields": (
                    "guardian_name",
                    "guardian_number",
                    "relationship_with_student",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "middle_name",
        "last_name",
        "username",
        "email",
        "phone",
        "gender",
        "qualification",
        "specialization_on",
        "marital_status",
        "date_of_joining",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "first_name",
        "middle_name",
        "last_name",
        "email",
        "phone",
        "username",
        "specialization_on",
    )
    list_filter = (
        "gender",
        "qualification",
        "marital_status",
        "date_of_joining",
    )
    list_editable = ("phone", "email", "gender", "marital_status")
    date_hierarchy = "date_of_joining"
    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "dob",
                    "gender",
                    "marital_status",
                    "address",
                )
            },
        ),
        ("Contact Information", {"fields": ("username", "password", "phone", "email")}),
        (
            "Professional Details",
            {"fields": ("qualification", "specialization_on", "date_of_joining")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "course_type", "duration", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("course_type",)
    readonly_fields = ("created_at", "updated_at")

    def changelist_view(self, request, extra_context=None):
        return redirect(reverse("manage_course"))


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "course", "duration", "created_at", "updated_at")
    search_fields = ("name", "course__name")
    list_filter = ("course__course_type", "course__duration")
    readonly_fields = ("created_at", "updated_at")

    def changelist_view(self, request, extra_context=None):
        return redirect(reverse("manage_subject"))
