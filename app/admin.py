from django.contrib import admin
from app.models import (
    Institute,
    Course,
    Subject,
    Student,
    Staff,
    Batch,
    Attendance,
    AttendanceRecord,
    Notice,
    Routine,
    StudentRoutine,
    Staff_leave,
    Student_Leave,
    StudentFeedback,
    CourseTracking,
)
from django.forms import ModelForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from app.forms import StaffAdminForm, StudentAdminForm
# Register your models here.


class CustomAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        # Original app list
        app_list = super().get_app_list(request)

        model_map = {
            "User": {
                "group": "Authentication",
                "group_label": "authentication",
            },
            "Group": {
                "group": "Authentication",
                "group_label": "authentication",
            },
            "Institute": {"group": "Organization", "group_label": "organization"},
            "Batch": {"group": "Organization", "group_label": "organization"},
            "Notice": {"group": "Organization", "group_label": "organization"},
            "Course": {"group": "Organization", "group_label": "organization"},
            "Subject": {"group": "Organization", "group_label": "organization"},
            "Student": {"group": "Human Management", "group_label": "human_management"},
            "Staff": {"group": "Human Management", "group_label": "human_management"},
            "Routine": {"group": "Human Management", "group_label": "human_management"},
            "Staff_leave": {"group": "Human Management", "group_label": "human_management"},
            "Student_Leave": {"group": "Human Management", "group_label": "human_management"},
            "StudentFeedback": {"group": "Human Management", "group_label": "human_management"},
            "CourseTracking": {"group": "Human Management", "group_label": "human_management"},
            "Attendance": {
                "group": "Human Management",
                "group_label": "human_management",
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

        grouped_app_list = list(grouped_models.values())

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
    list_display = ("id", "name", "duration", "duration_type")
    search_fields = ("name", "duration", "duration_type")
    list_filter = ("name", "duration", "duration_type")
    advanced_filter_fields = ("name", "duration", "duration_type")


@admin.register(Batch, site=custom_admin_site)
class BatchAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date")
    search_fields = ("name", "start_date", "end_date")
    list_filter = ("name", "start_date", "end_date")
    advanced_filter_fields = ("name", "start_date", "end_date")


@admin.register(Subject, site=custom_admin_site)
class SubjectModel(admin.ModelAdmin):
    list_display = ("id", "name", "course", "semester_or_year")
    search_fields = ("name", "course_id", "semester_or_year")
    list_filter = ("name", "course_id", "semester_or_year")


@admin.register(Student, site=custom_admin_site)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "phone")
    form = StudentAdminForm
    search_fields = (
        "name",
        "phone",
        "courses",
        "gender",
        "joining_date",
    )
    list_filter = (
        "name",
        "phone",
        "courses",
        "gender",
        "joining_date",
        "status",
    )
    advanced_filter_fields = (
        "name",
        "phone",
        "courses",
        "gender",
        "joining_date",
        "status",
    )
    readonly_fields = ("password",)
    ordering = ("name",)
    filter_horizontal = ("groups",)

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

    class Media:
        js = ("js/student_admin.js",)


@admin.register(Staff, site=custom_admin_site)
class StaffAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "designation", "joining_date"]
    form = StaffAdminForm
    search_fields = (
        "name",
        "phone",
        "monthly_salary",
        "designation",
        "joining_date",
        "gender",
    )
    list_filter = (
        "name",
        "phone",
        "designation",
        "joining_date",
        "gender",
        "groups",
    )
    advanced_filter_fields = (
        "name",
        "phone",
        "designation",
        "joining_date",
        "gender",
        "groups",
    )
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

    class Media:
        js = ("js/staff_admin.js",)


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

    class Media:
        js = ("js/attendance_admin.js",)


@admin.register(Notice, site=custom_admin_site)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "message", "created_at")
    search_fields = ("title", "message")
    list_filter = ("title", "message")
    advanced_filter_fields = ("title", "message")

    class Media:
        js = ("js/notice_admin.js",)


class StudentRoutineStackInline(admin.StackedInline):
    model = StudentRoutine
    extra = 0


@admin.register(Routine, site=custom_admin_site)
class RoutineAdmin(admin.ModelAdmin):
    inlines = [StudentRoutineStackInline]
    list_display = ["name", "start_time", "end_time", "teacher"]
    search_fields = ("name", "start_time", "end_time", "teacher__name")
    list_filter = ("name", "start_time", "end_time", "teacher")
    advanced_filter_fields = ("name", "start_time", "end_time", "teacher")

    class Media:
        js = ("js/multiple_student_hover.js", "js/routine_admin.js")


@admin.register(Staff_leave, site=custom_admin_site)
class StaffLeaveAdmin(admin.ModelAdmin):
    list_display = ('staff', 'date', 'get_status_display', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('staff__name', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    raw_id_fields = ('staff',)


@admin.register(Student_Leave, site=custom_admin_site)
class StudentLeaveAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'get_status_display', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('student__name', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    raw_id_fields = ('student',)


@admin.register(StudentFeedback, site=custom_admin_site)
class StudentFeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'rating', 'created_at')
    list_filter = ('rating',  'created_at')
    search_fields = ('student__name',  'feedback_text')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(CourseTracking, site=custom_admin_site)
class CourseTrackingAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'progress_status', 'completion_percentage', 'start_date', 'expected_end_date')
    list_filter = ('progress_status', 'course', 'start_date', 'expected_end_date')
    search_fields = ('student__name', 'course__name', 'notes')
    readonly_fields = ('enrollment_date', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    raw_id_fields = ('student', 'course')
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

    class Media:
        js = ("js/course_tracking_admin.js",)




custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)
