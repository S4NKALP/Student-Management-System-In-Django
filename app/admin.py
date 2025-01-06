from django.contrib import admin
from app.models import Teacher, Student, Staff, Course, AcademicYear, Subject, NewsEvent


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "phone", "active_status")
    search_fields = ("first_name", "last_name", "email", "phone")
    list_filter = ("active_status", "gender", "group")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "course",
        "academic_year",
        "active_status",
    )
    search_fields = ("first_name", "last_name", "email", "phone")
    list_filter = ("active_status", "gender", "course", "academic_year")


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "position",
        "active_status",
    )
    search_fields = ("first_name", "last_name", "email", "phone")
    list_filter = ("active_status", "position", "group")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "course_type", "duration")
    search_fields = ("name",)
    list_filter = ("course_type",)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("id", "batch")
    search_fields = ("batch",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "course", "semester_or_year_number")
    search_fields = ("name", "course__name")
    list_filter = ("course", "semester_or_year_number")


@admin.register(NewsEvent)
class NewsEventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "type", "created_at")
    search_fields = ("title", "summary")
    list_filter = ("type", "created_at")
