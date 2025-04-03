from django.contrib import admin
from .models import (
    Institute,
    Course,
    Subject,
    SubjectFile,
    Student,
    Staff,
    Batch,
    Attendance,
    AttendanceRecord,
    Notice,
    Routine,
    Staff_leave,
    Student_Leave,
    StudentFeedback,
    CourseTracking,
    InstituteFeedback,
    StaffInstituteFeedback,
    TOTPSecret,
    ResetToken,
)
from .firebase import FCMDevice
from django.forms import ModelForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from app.forms import StaffAdminForm, StudentAdminForm
from django.urls import path
from django.http import JsonResponse
import json
from django.db import transaction
from django.db.models import Q
from datetime import datetime

# Register your models here.


class CustomAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        # Original app list
        app_list = super().get_app_list(request)

        model_map = {
            # Authentication Models
            "User": {
                "group": "Authentication",
                "group_label": "authentication",
            },
            "Group": {
                "group": "Authentication",
                "group_label": "authentication",
            },
            "TOTPSecret": {
                "group": "Authentication",
                "group_label": "authentication",
            },
            "ResetToken": {
                "group": "Authentication",
                "group_label": "authentication",
            },
            # Organization Models
            "Institute": {
                "group": "Organization",
                "group_label": "organization",
            },
            "Batch": {
                "group": "Organization",
                "group_label": "organization",
            },
            "Notice": {
                "group": "Organization",
                "group_label": "organization",
            },
            # Course Management Models
            "Course": {
                "group": "Course Management",
                "group_label": "course_management",
            },
            "Subject": {
                "group": "Course Management",
                "group_label": "course_management",
            },
            "SubjectFile": {
                "group": "Course Management",
                "group_label": "course_management",
            },
            "CourseTracking": {
                "group": "Course Management",
                "group_label": "course_management",
            },
            # Human Management Models
            "Student": {
                "group": "Human Management",
                "group_label": "human_management",
            },
            "Staff": {
                "group": "Human Management",
                "group_label": "human_management",
            },
            "Routine": {
                "group": "Human Management",
                "group_label": "human_management",
            },
            "Staff_leave": {
                "group": "Human Management",
                "group_label": "human_management",
            },
            "Student_Leave": {
                "group": "Human Management",
                "group_label": "human_management",
            },
            # Attendance Models
            "Attendance": {
                "group": "Attendance",
                "group_label": "attendance",
            },
            "AttendanceRecord": {
                "group": "Attendance",
                "group_label": "attendance",
            },
            # Feedback Models
            "StudentFeedback": {
                "group": "Feedback",
                "group_label": "feedback",
            },
            "InstituteFeedback": {
                "group": "Feedback",
                "group_label": "feedback",
            },
            "StaffInstituteFeedback": {
                "group": "Feedback",
                "group_label": "feedback",
            },
            # Device Management
            "FCMDevice": {
                "group": "Device Management",
                "group_label": "device_management",
            },
        }

        grouped_app_list = [{"name": "Main", "app_label": "dashboard", "models": []}]
        grouped_models = {}

        for app in app_list:
            for model in app["models"]:
                model_name = model["object_name"]
                if model_name in model_map:
                    group = model_map[model_name]["group"]
                    if group not in grouped_models:
                        grouped_models[group] = {
                            "name": group,
                            "app_label": model_map[model_name]["group_label"],
                            "models": [],
                        }
                    grouped_models[group]["models"].append(model)

        dashboard_item = {
            "name": "Dashboard",
            "app_label": "dashboard",
            "models": [
                {
                    "name": "Dashboard",
                    "object_name": "Dashboard",
                    "perms": {"has_module_perms": True},
                    "admin_url": "/app/dashboard",
                    "view_only": True,
                }
            ],
        }

        grouped_app_list = [dashboard_item] + list(grouped_models.values())

        return grouped_app_list


# Create a custom admin site instance
custom_admin_site = CustomAdminSite(name="custom_admin")


@admin.register(Institute, site=custom_admin_site)
class InstituteModel(admin.ModelAdmin):
    list_display = ("id", "name", "address", "phone")
    search_fields = ("name", "phone")
    list_filter = ("name", "phone")
    advanced_filter_fields = ("name", "phone")


@admin.register(Course, site=custom_admin_site)
class CourseModel(admin.ModelAdmin):
    list_display = ("id", "name", "duration", "duration_type", "get_total_duration")
    search_fields = ("name", "duration", "duration_type")
    list_filter = ("duration_type", "duration")
    advanced_filter_fields = ("name", "duration", "duration_type")

    def get_total_duration(self, obj):
        if obj.duration_type == "Semester":
            return f"{obj.duration} years ({obj.duration * 2} semesters)"
        return f"{obj.duration} year{'s' if obj.duration > 1 else ''}"

    get_total_duration.short_description = "Total Duration"

    fieldsets = (
        (None, {"fields": ("name",)}),
        (
            "Duration Settings",
            {
                "fields": ("duration", "duration_type"),
                "description": "For yearly courses, duration is in years. For semester-based courses, duration is in years (2 semesters per year).",
            },
        ),
    )


@admin.register(Batch, site=custom_admin_site)
class BatchAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date")
    search_fields = ("name", "start_date", "end_date")
    list_filter = ("name", "start_date", "end_date")
    advanced_filter_fields = ("name", "start_date", "end_date")


@admin.register(Subject, site=custom_admin_site)
class SubjectModel(admin.ModelAdmin):
    list_display = ("id", "name", "course", "get_period_display", "has_syllabus", "file_count")
    search_fields = ("name", "course__name")
    list_filter = ("course", "semester_or_year")
    advanced_filter_fields = ("name", "course", "semester_or_year")

    def has_syllabus(self, obj):
        return bool(obj.syllabus_pdf)

    has_syllabus.boolean = True
    has_syllabus.short_description = "Has Syllabus"
    
    def file_count(self, obj):
        return obj.subjectfile_set.count()
    
    file_count.short_description = "Additional Files"

    def get_period_display(self, obj):
        if obj.course.duration_type == "Semester":
            return f"Semester {obj.semester_or_year}"
        return f"Year {obj.semester_or_year}"

    get_period_display.short_description = "Period"

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_save_and_add_another"] = True
        extra_context["show_save"] = False
        return super().add_view(request, form_url, extra_context)

    def response_add(self, request, obj, post_url_continue=None):
        if "_addanother" in request.POST:
            # Pre-fill the course and semester fields for the next entry
            return self.response_post_save_add(request, obj)
        return super().response_add(request, obj, post_url_continue)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.course:
            if obj.course.duration_type == "Semester":
                form.base_fields["semester_or_year"].label = "Semester"
                form.base_fields[
                    "semester_or_year"
                ].help_text = f"Enter semester number (1-{obj.course.duration * 2})"
            else:
                form.base_fields["semester_or_year"].label = "Year"
                form.base_fields[
                    "semester_or_year"
                ].help_text = f"Enter year number (1-{obj.course.duration})"

        # Keep the last used course selected for next entry
        if not obj and request.method == "GET":
            if "course" in request.GET:
                form.base_fields["course"].initial = request.GET["course"]
            if "semester_or_year" in request.GET:
                form.base_fields["semester_or_year"].initial = request.GET[
                    "semester_or_year"
                ]
        return form

    def response_post_save_add(self, request, obj):
        from django.http import HttpResponseRedirect
        from django.urls import reverse

        opts = self.model._meta
        url = reverse(f"admin:{opts.app_label}_{opts.model_name}_add")
        return HttpResponseRedirect(
            f"{url}?course={obj.course.id}&semester_or_year={obj.semester_or_year}"
        )


@admin.register(Student, site=custom_admin_site)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ("id", "name", "phone", "course", "status")
    search_fields = ("name", "phone", "course__name")
    list_filter = ("course", "status", "gender", "joining_date")
    advanced_filter_fields = ("name", "phone", "course", "batch", "status")

    def has_view_permission(self, request, obj=None):
        """Check if user has view permission"""
        return request.user.has_perm("app.view_student")

    def has_add_permission(self, request):
        """Check if user has add permission"""
        return request.user.has_perm("app.add_student")

    def has_change_permission(self, request, obj=None):
        """Check if user has change permission"""
        return request.user.has_perm("app.change_student")

    def has_delete_permission(self, request, obj=None):
        """Check if user has delete permission"""
        return request.user.has_perm("app.delete_student")

    def has_module_permission(self, request):
        """Check if user has any permissions for this app"""
        return request.user.has_module_perms("app")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("password",)
        return self.readonly_fields


@admin.register(Staff, site=custom_admin_site)
class StaffAdmin(admin.ModelAdmin):
    form = StaffAdminForm
    list_display = ("id", "name", "phone", "designation", "joining_date")
    search_fields = ("name", "phone", "designation")
    list_filter = ("designation", "joining_date", "gender")
    advanced_filter_fields = ("name", "phone", "designation")
    readonly_fields = ("password",)
    ordering = ("name",)
    filter_horizontal = ("groups",)

    def has_view_permission(self, request, obj=None):
        """Check if user has view permission"""
        return request.user.has_perm("app.view_staff")

    def has_add_permission(self, request):
        """Check if user has add permission"""
        return request.user.has_perm("app.add_staff")

    def has_change_permission(self, request, obj=None):
        """Check if user has change permission"""
        return request.user.has_perm("app.change_staff")

    def has_delete_permission(self, request, obj=None):
        """Check if user has delete permission"""
        return request.user.has_perm("app.delete_staff")

    def has_module_permission(self, request):
        """Check if user has any permissions for this app"""
        return request.user.has_module_perms("app")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("password",)
        return self.readonly_fields


class AttendanceRecordForm(ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("student"):
            if self.instance and self.instance.pk:
                cleaned_data["student"] = self.instance.student
        return cleaned_data

    class Meta:
        model = AttendanceRecord
        fields = "__all__"


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    form = AttendanceRecordForm
    extra = 0
    can_delete = False  # Prevent deletion

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        return formset


@admin.register(Attendance, site=custom_admin_site)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ["date", "routine", "class_status", "teacher", "teacher_attend"]
    inlines = [AttendanceRecordInline]
    search_fields = ("date", "routine__name", "teacher__name")
    list_filter = ("date", "routine", "teacher")
    advanced_filter_fields = ("date", "routine", "teacher")

    def save_model(self, request, obj, form, change):
        is_new = not obj.pk
        super().save_model(request, obj, form, change)

        if is_new and obj.routine:
            students = Student.objects.filter(routines__routine=obj.routine).distinct()

            for student in students:
                AttendanceRecord.objects.create(
                    attendance=obj, student=student, student_attend=False
                )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        # Preserve existing records
        for instance in instances:
            if instance.pk and not instance.student_id:
                original = AttendanceRecord.objects.get(pk=instance.pk)
                instance.student = original.student
            instance.save()

        formset.save_m2m()


@admin.register(Notice, site=custom_admin_site)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "message", "created_at")
    search_fields = ("title", "message")
    list_filter = ("title", "message")
    advanced_filter_fields = ("title", "message")


@admin.register(Routine, site=custom_admin_site)
class RoutineAdmin(admin.ModelAdmin):
    list_display = [
        "course",
        "subject",
        "teacher",
        "start_time",
        "end_time",
        "semester_or_year",
        "is_active",
    ]
    list_filter = ["is_active", "course", "subject", "teacher", "semester_or_year"]
    search_fields = ["course__name", "subject__name", "teacher__name"]
    ordering = ["start_time"]
    change_form_template = "admin/app/routine/change_form.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "add-multiple/",
                self.admin_site.admin_view(self.save_routines),
                name="routine-add-multiple",
            ),
        ]
        return custom_urls + urls

    def save_routines(self, request):
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                routines = data.get("routines", [])

                if not routines:
                    return JsonResponse(
                        {"success": False, "message": "No routines data provided"}
                    )

                with (
                    transaction.atomic()
                ):  # Use transaction to ensure all routines are created or none
                    created_routines = []
                    for index, routine_data in enumerate(routines):
                        try:
                            # Validate required fields
                            required_fields = [
                                "course",
                                "subject",
                                "teacher",
                                "start_time",
                                "end_time",
                                "semester_or_year",
                            ]
                            missing_fields = [
                                field
                                for field in required_fields
                                if field not in routine_data
                                or not routine_data.get(field)
                            ]

                            if missing_fields:
                                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                                raise ValueError(error_msg)

                            # Convert IDs to integers
                            try:
                                course_id = int(routine_data["course"])
                                subject_id = int(routine_data["subject"])
                                teacher_id = int(routine_data["teacher"])
                                semester = int(routine_data["semester_or_year"])

                            except (ValueError, TypeError) as e:
                                raise ValueError(f"Error parsing IDs: {str(e)}")

                            # Validate time format
                            try:
                                start_time = datetime.strptime(
                                    routine_data["start_time"], "%H:%M"
                                ).time()
                                end_time = datetime.strptime(
                                    routine_data["end_time"], "%H:%M"
                                ).time()
                            except ValueError as e:
                                raise ValueError(
                                    "Invalid time format. Please use HH:MM format."
                                )

                            # Check for existing routine
                            existing_routine = Routine.objects.filter(
                                course_id=course_id,
                                subject_id=subject_id,
                                semester_or_year=semester,
                                start_time=start_time,
                                end_time=end_time,
                            ).first()

                            if existing_routine:
                                # Update existing routine
                                existing_routine.teacher_id = teacher_id
                                existing_routine.save()
                                created_routines.append(existing_routine)
                            else:
                                # Create new routine
                                routine = Routine.objects.create(
                                    course_id=course_id,
                                    subject_id=subject_id,
                                    teacher_id=teacher_id,
                                    start_time=start_time,
                                    end_time=end_time,
                                    semester_or_year=semester,
                                    is_active=True,
                                )
                                created_routines.append(routine)

                        except ValueError as e:
                            raise  # Re-raise to trigger rollback
                        except Exception as e:
                            raise  # Re-raise to trigger rollback

                    return JsonResponse(
                        {
                            "success": True,
                            "message": f"Successfully saved {len(created_routines)} routines",
                            "routines": [
                                {
                                    "id": r.id,
                                    "course": r.course.name,
                                    "subject": r.subject.name,
                                    "teacher": r.teacher.name,
                                    "start_time": r.start_time.strftime("%H:%M"),
                                    "end_time": r.end_time.strftime("%H:%M"),
                                    "semester_or_year": r.semester_or_year,
                                }
                                for r in created_routines
                            ],
                        }
                    )

            except ValueError as e:
                return JsonResponse({"success": False, "message": str(e)})
            except json.JSONDecodeError as e:
                return JsonResponse(
                    {"success": False, "message": f"Invalid JSON data: {str(e)}"}
                )
            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)})

        return JsonResponse({"success": False, "message": "Invalid request method"})

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "subject":
            if request.GET.get("course"):
                kwargs["queryset"] = Subject.objects.filter(
                    course_id=request.GET.get("course"),
                    semester_or_year=request.GET.get("semester_or_year", 1),
                )
            else:
                kwargs["queryset"] = Subject.objects.none()
        elif db_field.name == "teacher":
            kwargs["queryset"] = Staff.objects.filter(
                Q(designation__icontains="Teacher")
                | Q(designation__icontains="Staff")
                | Q(designation__icontains="Principal")
                | Q(designation__isnull=True)
                | Q(designation="")
            ).order_by("name")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Only for adding new routines
            form.base_fields["course"].widget.attrs["class"] = "select2"
            form.base_fields["subject"].widget.attrs["class"] = "select2"
            form.base_fields["teacher"].widget.attrs["class"] = "select2"
            form.base_fields["semester_or_year"].initial = 1
        return form

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_save_and_add_another"] = True
        return super().add_view(request, form_url, extra_context)

    class Media:
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css",
            )
        }
        js = ("https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js",)


@admin.register(Staff_leave, site=custom_admin_site)
class StaffLeaveAdmin(admin.ModelAdmin):
    list_display = ("staff", "start_date", "end_date", "get_status_display", "created_at")
    list_filter = ("status", "start_date", "end_date", "created_at")
    search_fields = ("staff__name", "message")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    raw_id_fields = ("staff",)


@admin.register(Student_Leave, site=custom_admin_site)
class StudentLeaveAdmin(admin.ModelAdmin):
    list_display = ("student", "start_date", "end_date", "get_status_display", "created_at")
    list_filter = ("status", "start_date", "end_date", "created_at")
    search_fields = ("student__name", "message")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    raw_id_fields = ("student",)


@admin.register(StudentFeedback, site=custom_admin_site)
class StudentFeedbackAdmin(admin.ModelAdmin):
    list_display = ("student", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("student__name", "feedback_text")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(CourseTracking, site=custom_admin_site)
class CourseTrackingAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course",
        "progress_status",
        "completion_percentage",
        "start_date",
        "expected_end_date",
    )
    list_filter = ("progress_status", "course", "start_date", "expected_end_date")
    search_fields = ("student__name", "course__name", "notes")
    readonly_fields = ("enrollment_date", "created_at", "updated_at")
    ordering = ("-created_at",)
    raw_id_fields = ("student", "course")
    list_per_page = 25

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm("app.view_coursetracking")

    def has_add_permission(self, request):
        return request.user.has_perm("app.add_coursetracking")

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm("app.change_coursetracking")

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm("app.delete_coursetracking")

    def has_module_permission(self, request):
        return request.user.has_module_perms("app")


@admin.register(InstituteFeedback, site=custom_admin_site)
class InstituteFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "institute",
        "feedback_type",
        "rating",
        "is_anonymous",
        "is_public",
        "created_at",
    )
    list_filter = (
        "feedback_type",
        "rating",
        "is_anonymous",
        "is_public",
        "created_at",
        "institute",
    )
    search_fields = ("user__name", "institute__name", "feedback_text")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"

    def display_name(self, obj):
        return obj.display_name

    display_name.short_description = "Student Name"

    fieldsets = (
        (None, {"fields": ("institute", "user")}),
        (
            "Feedback Details",
            {
                "fields": (
                    "feedback_type",
                    "rating",
                    "feedback_text",
                    "is_anonymous",
                    "is_public",
                )
            },
        ),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "institute")

    class Media:
        css = {"all": ("admin/css/forms.css",)}
        js = ("admin/js/collapse.js",)


@admin.register(StaffInstituteFeedback, site=custom_admin_site)
class StaffInstituteFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "institute",
        "feedback_type",
        "rating",
        "is_anonymous",
        "is_public",
        "created_at",
    )
    list_filter = (
        "feedback_type",
        "rating",
        "is_anonymous",
        "is_public",
        "created_at",
        "institute",
    )
    search_fields = ("staff__name", "institute__name", "feedback_text")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"

    def display_name(self, obj):
        return obj.display_name

    display_name.short_description = "Staff Name"

    fieldsets = (
        (None, {"fields": ("institute", "staff")}),
        (
            "Feedback Details",
            {
                "fields": (
                    "feedback_type",
                    "rating",
                    "feedback_text",
                    "is_anonymous",
                    "is_public",
                )
            },
        ),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("staff", "institute")


@admin.register(FCMDevice, site=custom_admin_site)
class FCMDeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "token", "created_at", "last_active", "is_active")
    search_fields = ("token",)
    list_filter = ("is_active", "created_at", "last_active")
    readonly_fields = ("created_at", "last_active")
    ordering = ("-last_active",)

    fieldsets = (
        (None, {"fields": ("token", "is_active")}),
        ("Metadata", {"fields": ("created_at", "last_active"), "classes": ("collapse",)}),
    )


@admin.register(SubjectFile, site=custom_admin_site)
class SubjectFileAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "subject", "uploaded_by", "uploaded_at")
    search_fields = ("title", "subject__name", "uploaded_by__name")
    list_filter = ("subject__course", "uploaded_at")
    autocomplete_fields = ["subject", "uploaded_by"]


custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)
