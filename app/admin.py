from django import forms
from django.contrib import admin
from django.db.models import Max
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.translation import gettext_lazy as _

from app.forms import SubjectForm
from app.models import (
    AcademicYear,
    Attendance,
    Certificate,
    ClassRoutine,
    Complaint,
    Course,
    Library,
    Marksheet,
    NewsEvent,
    Notes,
    Staff,
    Student,
    Subject,
    SubjectMark,
    Teacher,
    TeacherLeave,
    StudentLeave,
    FeedbackStudent,
    FeedbackTeacher,
)

admin.site.register(Notes)
admin.site.register(StudentLeave)
admin.site.register(TeacherLeave)
admin.site.register(FeedbackStudent)
admin.site.register(FeedbackTeacher)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    pass

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.complaint_list_view, name="complaint_changelist"),
        ]
        return custom_urls + urls

    def complaint_list_view(self, request):
        complaints = Complaint.objects.all()
        context = {
            **self.admin_site.each_context(request),
            "title": "Complaint List",
            "complaints": complaints,
            "opts": self.model._meta,
            "has_add_permission": self.has_add_permission(request),
        }
        return TemplateResponse(request, "Hod/complaint.html", context)


# BaseUserAdmin to handle common behavior for BaseUser-based models
class BaseUserAdmin(admin.ModelAdmin):
    exclude = [
        "user",
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.user:
            obj.user.groups.set(obj.group.all())
            obj.user.save()


@admin.register(Teacher)
class TeacherAdmin(BaseUserAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "gender",
        "qualification",
        "specialization",
    )
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
class StudentAdmin(BaseUserAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "course",
        "academic_year",
    )
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
class StaffAdmin(BaseUserAdmin):
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
        academic_years = AcademicYear.objects.all().order_by("year")

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
    form = SubjectForm
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
        course_id = request.GET.get("course")
        semester_or_year = request.GET.get("semester_or_year_number")

        subjects = Subject.objects.all().select_related("course", "teacher")
        courses = Course.objects.all()

        if course_id:
            subjects = subjects.filter(course_id=course_id)
        if semester_or_year:
            subjects = subjects.filter(semester_or_year_number=semester_or_year)

        periods = []
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
                period_type = "Semester" if course.course_type == "semester" else "Year"
                periods = [
                    {"number": str(i), "display": f"{period_type} {i}"}
                    for i in range(1, course.duration + 1)
                ]
            except Course.DoesNotExist:
                pass

        context = {
            **self.admin_site.each_context(request),
            "title": "Subjects",
            "subjects": subjects,
            "opts": self.model._meta,
            "courses": courses,
            "periods": periods,
            "selected_course": course_id,
            "selected_period": semester_or_year,
            "has_add_permission": self.has_add_permission(request),
        }
        return TemplateResponse(request, "Hod/subject.html", context)

    class Media:
        js = ("dist/js/update_period.js",)


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
        attendance_records = (
            Attendance.objects.select_related("student", "subject")
            .all()
            .order_by("-date")
        )
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
    list_display = (
        "book_name",
        "category",
        "publication",
        "publication_year",
        "quantity",
        "available",
        "date_added",
    )
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
        "subject",
        "obtained_practical_marks",
        "total_practical_marks",
        "obtained_theory_marks",
        "total_theory_marks",
        "total_marks",
    )
    readonly_fields = ("total_marks",)  # Make total_marks read-only

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

    class Media:
        js = "js/marksheet_admin.js"

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


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("student", "date")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("", self.certificate_list_view, name="certificate_changelist"),
        ]
        return custom_urls + urls

    def certificate_list_view(self, request):
        certificates = Certificate.objects.all()
        context = {
            **self.admin_site.each_context(request),
            "title": "Certificate List",
            "certificates": certificates,
            "opts": self.model._meta,
            "has_add_permission": self.has_add_permission(request),
        }
        return TemplateResponse(request, "Hod/certificate.html", context)


@admin.register(ClassRoutine)
class ClassRoutineAdmin(admin.ModelAdmin):
    pass
