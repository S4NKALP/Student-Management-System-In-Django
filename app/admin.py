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


@admin.register(LeaveReportStudent)
class LeaveReportStudentAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse("student_leave_view"))


@admin.register(LeaveReportTeacher)
class LeaveReportTeacherAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse("teacher_leave_view"))


@admin.register(FeedbackTeacher)
class FeedbackTeacherAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse("teacher_feedback"))


@admin.register(FeedbackStudent)
class FeedbackStudentAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse("student_feedback_message"))


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse("manage_academicyear"))


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse("admin_view_attendance"))


@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    pass


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse("manage_student"))


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse("manage_teacher"))


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
