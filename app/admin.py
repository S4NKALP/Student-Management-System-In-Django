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
    Marksheet,
    Library,
    Marksheet,
    # Certificate,
    SubjectMark,

)
from django.shortcuts import render
from django.urls import path
from django.template.response import TemplateResponse


# BaseUserAdmin to handle common behavior for BaseUser-based models
class BaseUserAdmin(admin.ModelAdmin):
    exclude = ["user"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.user:
            obj.user.groups.set(obj.group.all())
            obj.user.save()


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone", "gender", "qualification", "specialization")
    search_fields = ("first_name", "last_name", "email", "phone", "specialization")
    list_filter = ("gender", "qualification", "date_of_joining")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.teacher_list_view, name="teacher_changelist"),
        ]
        return custom_urls + urls

    def teacher_list_view(self, request):
        teachers = Teacher.objects.all()
        context = {
            **self.admin_site.each_context(request),
            "title": "Teacher List",
            "teachers": teachers,
            "opts": self.model._meta,
        }
        return TemplateResponse(request, "Hod/teacher.html", context)
    
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone", "course", "academic_year")
    search_fields = ("first_name", "last_name", "email", "phone", "course__name")
    list_filter = ("gender", "academic_year", "course")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.student_list_view, name="student_changelist"),
        ]
        return custom_urls + urls

    def student_list_view(self, request):
        students = Student.objects.select_related("course", "academic_year").all()
        context = {
            **self.admin_site.each_context(request),
            "title": "Student List",
            "students": students,
            "opts": self.model._meta,
        }
        return TemplateResponse(request, "Hod/student.html", context)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "position", "date_of_joining")
    search_fields = ("first_name", "last_name", "email", "position")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.staff_list_view, name="staff_list"),
        ]
        return custom_urls + urls

    def staff_list_view(self, request):
        staff_members = Staff.objects.all()
        context = {
            **self.admin_site.each_context(request),
            "title": "Staff List",
            "staff_members": staff_members,
        }
        return TemplateResponse(request, "Hod/staff.html", context)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "course_type", "duration")
    list_filter = ("level", "course_type")
    search_fields = ("name",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.course_list_view, name="course_changelist"),
        ]
        return custom_urls + urls

    def course_list_view(self, request):
        # Get all courses
        courses = Course.objects.all().order_by("name")

        # Prepare the context with your model's specific fields
        context = {
            **self.admin_site.each_context(request),
            "title": "Course List",
            "courses": courses,
            "opts": self.model._meta,
            "has_add_permission": self.has_add_permission(request),
            "level_choices": dict(Course.level_choice),
            "course_type_choices": dict(
                [("semester", "Semester-based"), ("yearly", "Yearly-based")]
            ),
        }

        return TemplateResponse(request, "Hod/add_course.html", context)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("id", "year")
    search_fields = ("year",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.academic_year_list_view, name="academic_year_changelist"),
        ]
        return custom_urls + urls

    def academic_year_list_view(self, request):
        # Get all academic years
        academic_years = AcademicYear.objects.all().order_by("year")

        # Prepare the context with your model's specific fields
        context = {
            **self.admin_site.each_context(request),
            "title": "Academic List",
            "academic_years": academic_years,
            "opts": self.model._meta,
            "has_add_permission": self.has_add_permission(request),
        }

        return TemplateResponse(request, "Hod/academic_year.html", context)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "semester_or_year_number", "teacher")
    search_fields = ("name", "course__name", "teacher__name")
    list_filter = ("course", "semester_or_year_number")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.subject_list_view, name="subject_changelist"),
        ]
        return custom_urls + urls

    def subject_list_view(self, request):
        subjects = Subject.objects.select_related("course", "teacher").all().order_by("course__name", "semester_or_year_number")
        context = {
            **self.admin_site.each_context(request),
            "title": "Subjects",
            "subjects": subjects,
            "opts": self.model._meta,
            "has_add_permission": self.has_add_permission(request),
        }
        return TemplateResponse(request, "Hod/subject.html", context)



@admin.register(NewsEvent)
class NewsEventAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "created_at")
    search_fields = ("title", "summary", "type")
    list_filter = ("type", "created_at")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.news_event_list_view, name="newsevent_changelist"),
        ]
        return custom_urls + urls

    def news_event_list_view(self, request):
        news_events = NewsEvent.objects.all().order_by("-created_at")
        context = {
            **self.admin_site.each_context(request),
            "title": "News and Events",
            "news_events": news_events,
            "opts": self.model._meta,
            "has_add_permission": self.has_add_permission(request),
        }
        return TemplateResponse(request, "Hod/news_events.html", context)



@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "date", "status")
    search_fields = ("student__name", "subject__name", "status")
    list_filter = ("status", "date", "subject")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.attendance_list_view, name="attendance_changelist"),
        ]
        return custom_urls + urls

    def attendance_list_view(self, request):
        attendance_records = Attendance.objects.select_related("student", "subject").all().order_by("-date")
        context = {
            **self.admin_site.each_context(request),
            "title": "Attendance Records",
            "attendance_records": attendance_records,
            "opts": self.model._meta,
            "has_add_permission": self.has_add_permission(request),
        }
        return TemplateResponse(request, "Hod/attendance.html", context)



# admin.site.register()


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ("book_name", "category", "publication", "publication_year", "quantity", "available", "date_added")
    search_fields = ("book_name", "category", "publication")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.library_list_view, name="library_changelist"),
        ]
        return custom_urls + urls

    def library_list_view(self, request):
        books = Library.objects.all().order_by("-date_added")
        context = {
            **self.admin_site.each_context(request),
            "title": "Library",
            "books": books,
            "opts": self.model._meta,
            "has_add_permission": self.has_add_permission(request),
        }
        return TemplateResponse(request, "Hod/library.html", context)


class SubjectMarkInline(admin.TabularInline):
    model = SubjectMark
    extra = 1


class SubjectMarkInline(admin.TabularInline):
    model = SubjectMark
    extra = 1  # Number of extra forms to display
    fields = (
        'subject',
        'obtained_practical_marks',
        'total_practical_marks',
        'obtained_theory_marks',
        'total_theory_marks',
        'total_marks',
    )
    readonly_fields = ('total_marks',)  # Make total_marks read-only

    def save_related(self, request, formset, change):
        super().save_related(request, formset, change)
        for marksheet in formset.instance:
            marksheet.save()  # Ensure the Marksheet instance saves after each inline

@admin.register(Marksheet)
class MarksheetAdmin(admin.ModelAdmin):
    inlines = [SubjectMarkInline]
    list_display = ("student", "course", "total_marks", "obtained_marks", "grade")
    list_filter = ("course", "grade")
    search_fields = ("student__first_name", "student__last_name", "course__name")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.marksheet_list_view, name="marksheet_changelist"),
        ]
        return custom_urls + urls

    def marksheet_list_view(self, request):
        marksheets = Marksheet.objects.select_related("student", "course").all()
        context = {
            **self.admin_site.each_context(request),
            "title": "Marksheet List",
            "marksheets": marksheets,
            "opts": self.model._meta,
            "has_add_permission": self.has_add_permission(request),
        }
        return TemplateResponse(request, "Hod/marksheet.html", context)
    
# @admin.register(Certificate)
# class CertificateAdmin(admin.ModelAdmin):
#     list_display = ("title", "student", "course", "issued_date", "is_verified")
#     search_fields = ("student__first_name", "student__last_name", "course__name", "title")
#     list_filter = ("is_verified", "issued_date")

#     # Optionally, you can add actions for verification or custom actions
#     actions = ["mark_verified", "mark_unverified"]

#     def mark_verified(self, request, queryset):
#         queryset.update(is_verified=True)

#     def mark_unverified(self, request, queryset):
#         queryset.update(is_verified=False)

#     mark_verified.short_description = "Mark selected certificates as verified"
#     mark_unverified.short_description = "Mark selected certificates as unverified"    
