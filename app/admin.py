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
    Library,
    Marksheet,
    SubjectMark,
)


# BaseUserAdmin to handle common behavior for BaseUser-based models
class BaseUserAdmin(admin.ModelAdmin):
    exclude = ["user"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.user:
            obj.user.groups.set(obj.group.all())
            obj.user.save()


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
        "father_name",
        "mother_name",
        "guardian_name",
        "email",
        "phone",
        "course",
        "academic_year",
        "active_status",
    )
    search_fields = (
        "first_name",
        "last_name",
        "father_name",
        "mother_name",
        "email",
        "phone",
    )
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
    list_display = ("id", "name", "level", "course_type", "duration")
    search_fields = ("name",)
    list_filter = ("course_type",)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("id", "year")
    search_fields = ("year",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "course", "semester_or_year_number")
    search_fields = ("name", "course__name")
    list_filter = ("course", "semester_or_year_number")


@admin.register(NewsEvent)
class NewsEventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "summary", "type", "created_at")
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


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ("book_name", "publication", "publication_year", "available")


class SubjectMarkInline(admin.TabularInline):
    model = SubjectMark
    extra = 1
    fields = (
        "subject",
        "obtained_theory_marks",
        "total_theory_marks",
        "obtained_practical_marks",
        "total_practical_marks",
        "total_marks",
    )
    readonly_fields = ("total_marks",)


@admin.register(Marksheet)
class MarksheetAdmin(admin.ModelAdmin):
    inlines = [SubjectMarkInline]
    list_display = ["student", "course", "total_marks", "obtained_marks", "grade"]
    readonly_fields = ["total_marks", "obtained_marks", "grade"]


# class SubjectMarkInline(admin.TabularInline):
#     model = SubjectMark
#     extra = 1
#     fields = (
#         "subject",
#         "obtained_theory_marks",
#         "total_theory_marks",
#         "obtained_practical_marks",
#         "total_practical_marks",
#         "total_marks",
#     )
#     readonly_fields = ("total_marks",)
#
#
# @admin.register(Marksheet)
# class MarksheetAdmin(admin.ModelAdmin):
#     list_display = ["student", "course", "total_marks", "obtained_marks", "grade"]
#     list_filter = ["grade", "course"]
#     search_fields = ["student__first_name", "student__last_name", "course__name"]
#     readonly_fields = ["total_marks", "obtained_marks", "grade"]
#     inlines = [SubjectMarkInline]
#
#     fieldsets = (
#         ("Student Information", {"fields": ("student", "course")}),
#         (
#             "Results",
#             {
#                 "fields": ("total_marks", "obtained_marks", "grade"),
#                 "classes": ("collapse",),
#             },
#         ),
#     )
