from django.contrib import admin
from main.models import (
    Teacher,
    Student,
    Staff,
    Course,
    AcademicYear,
    Subject,
    NewsEvent,
)

# Register your models here.


class TeacherAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone", "active_status")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("gender", "active_status")


class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "course",
        "academic_year",
        "active_status",
    )
    search_fields = ("first_name", "last_name", "email", "phone")
    list_filter = ("gender", "course", "academic_year", "active_status")


class StaffAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "position",
        "active_status",
    )
    search_fields = ("first_name", "last_name", "email", "phone")
    list_filter = ("position", "active_status")


class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "course_type", "duration", "academic_year")
    search_fields = ("name",)
    list_filter = ("course_type", "academic_year")


class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("batch",)
    search_fields = ("batch",)


class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "semester_or_year_number")
    search_fields = ("name", "course__name")
    list_filter = ("course", "semester_or_year_number")


class NewsEventAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "created_at")
    search_fields = ("title", "summary")
    list_filter = ("type", "created_at")


# Register models with custom admin configurations
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(AcademicYear, AcademicYearAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(NewsEvent, NewsEventAdmin)
