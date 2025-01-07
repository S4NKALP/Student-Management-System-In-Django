from django.contrib import admin
from app.models import (
    Teacher,
    Student,
    Staff,
    Course,
    AcademicYear,
    Subject,
    NewsEvent,
    Attendance,
    Result,
)


class BaseUserAdmin(admin.ModelAdmin):
    exclude = ["user"]

    def save_model(self, request, obj, form, change):
        # Save the BaseUser instance
        super().save_model(request, obj, form, change)

        # Sync the groups with the related User object
        if obj.user:
            obj.user.groups.set(obj.group.all())  # Sync groups
            obj.user.save()  # Save the User object to persist changes


@admin.register(Teacher)
class TeacherAdmin(BaseUserAdmin):
    list_display = ("id", "first_name", "last_name", "email", "phone", "active_status")
    search_fields = ("first_name", "last_name", "email", "phone")
    list_filter = ("active_status", "gender", "group")


@admin.register(Student)
class StudentAdmin(BaseUserAdmin):
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
class StaffAdmin(BaseUserAdmin):
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


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "subject", "date", "status")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "subject",
        "practical_marks",
        "exam_marks",
        "total_marks",
    )
    readonly_fields = ("total_marks",)

    def save_model(self, request, obj, form, change):
        obj.total_marks = obj.get_total()
        super().save_model(request, obj, form, change)
