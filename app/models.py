from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

# Create your models here.
duration_types_choices = (("Year", "Yearl Based"), ("Semester", "Semester Based"))
student_status_choices = (
    ("Active", "Active"),
    ("Leave", "Leave"),
    ("Completed", "Completed"),
)
gender_choices = (("Male", "Male"), ("Female", "Female"), ("Other", "Other"))
marital_status_choices = (
    ("Married", "Married"),
    ("Unmarried", "Unmarried"),
    ("Divorced", "Divorced"),
)


class Institute(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    pan_no = models.CharField(max_length=255, null=True, blank=True)
    reg_no = models.CharField(max_length=255, null=True, blank=True)
    logo = models.ImageField(upload_to="image", null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Institute"
        verbose_name_plural = "Institutes"


class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=500)
    duration = models.IntegerField(default=1, null=True, blank=True)
    duration_type = models.CharField(
        max_length=255, choices=duration_types_choices, null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"


class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=1)
    semester_or_year = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Student(AbstractUser):
    first_name = None
    last_name = None
    is_superuser = None
    date_joined = None
    username = None
    email = None

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this student.",
        related_name="student_set",  # This fixes the clash
        related_query_name="student",
    )

    # Similarly, let's also update groups to be explicit
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this student belongs to.",
        related_name="students",  # This matches your existing related_name
    )

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=255, choices=student_status_choices, null=True, blank=True
    )
    gender = models.CharField(
        max_length=255, choices=gender_choices, null=True, blank=True
    )
    birth_date = models.DateField(null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True, unique=True)
    temporary_address = models.CharField(max_length=500, null=True, blank=True)
    permanent_address = models.CharField(max_length=500, null=True, blank=True)
    parent_name = models.CharField(max_length=255, null=True, blank=True)
    parent_phone = models.CharField(max_length=255, null=True, blank=True)
    courses = models.ManyToManyField(Course, related_name="students", blank=True)
    joining_date = models.DateField(null=True, blank=True)
    password = models.CharField(
        max_length=128, editable=False, null=True
    )  # Editable is set to False to prevent direct editing

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["name"]  # Add required fields

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save(update_fields=["password"])

    @property
    def is_staff(self):
        """Check if student has any groups (permissions)"""
        return self.groups.exists()

    def has_perm(self, perm, obj=None):
        """Check if student has a specific permission"""
        if not self.is_active:
            return False

        # Get permissions from groups
        perms = set()
        for group in self.groups.all():
            perms.update(
                group.permissions.values_list("content_type__app_label", "codename")
            )

        # Convert permission string to app_label and codename
        app_label, codename = perm.split(".")
        return (app_label, codename) in perms

    def has_module_perms(self, app_label):
        """Check if student has any permissions in the given app"""
        if not self.is_active:
            return False

        # Check if any group permissions match the app_label
        for group in self.groups.all():
            if group.permissions.filter(content_type__app_label=app_label).exists():
                return True
        return False

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"


class Staff(AbstractUser):
    first_name = None
    last_name = None
    date_joined = None
    username = None
    email = None
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this staff.",
        related_name="staff_set",  # This fixes the clash
        related_query_name="staff",
    )

    # Similarly, let's also update groups to be explicit
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this staff belongs to.",
        related_name="staffs",  # This matches your existing related_name
    )
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, null=True, blank=True, unique=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(
        max_length=255, choices=gender_choices, null=True, blank=True
    )
    birth_date = models.DateField(null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    temporary_address = models.CharField(max_length=255, null=True, blank=True)
    permanent_address = models.CharField(max_length=255, null=True, blank=True)
    marital_status = models.CharField(
        max_length=255, choices=marital_status_choices, null=True, blank=True
    )
    joining_date = models.DateField(null=True, blank=True)
    password = models.CharField(
        max_length=128, editable=False, null=True
    )  # Editable is set to False to prevent direct editing

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["name"]  # Add required fields

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save(update_fields=["password"])

    @property
    def is_staff(self):
        """Check if student has any groups (permissions)"""
        return True

    @property
    def is_authenticated(self):
        return True

    def has_perm(self, perm, obj=None):
        """Check if student has a specific permission"""
        if not self.is_active:
            return False

        # Get permissions from groups
        perms = set()
        for group in self.groups.all():
            perms.update(
                group.permissions.values_list("content_type__app_label", "codename")
            )

        # Convert permission string to app_label and codename
        app_label, codename = perm.split(".")
        return (app_label, codename) in perms

    def has_module_perms(self, app_label):
        """Check if student has any permissions in the given app"""
        if not self.is_active:
            return False

        # Check if any group permissions match the app_label
        for group in self.groups.all():
            if group.permissions.filter(content_type__app_label=app_label).exists():
                return True
        return False

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staffs"


class Batch(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Batch"
        verbose_name_plural = "Batches"


class Routine(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    teacher = models.ForeignKey(
        Staff, related_name="routines", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Routine"
        verbose_name_plural = "Routines"


class StudentRoutine(models.Model):
    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(
        Student, related_name="routines", on_delete=models.CASCADE, null=True
    )
    routine = models.ForeignKey(
        Routine, related_name="students", on_delete=models.CASCADE, null=True
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.student.name


class Attendance(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.DateField()
    routine = models.ForeignKey(
        Routine,
        related_name="attendances",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    teacher = models.ForeignKey(
        Staff,
        related_name="attendances",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    teacher_attend = models.BooleanField(default=True)
    class_status = models.BooleanField(default=True)

    def __str__(self):
        return str(self.date)

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"


class AttendanceRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="records",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attendance_records",
    )
    student_attend = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.student.name


class FCMDevice(models.Model):
    id = models.BigAutoField(primary_key=True)
    token = models.TextField(unique=True)

    def __str__(self):
        return self.token


class Notice(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="notice", blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        send_push_notification(
            self.title, self.message, FCMDevice.objects.values_list("token", flat=True)
        )
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Notice"
        verbose_name_plural = "Notices"


class Staff_leave(models.Model):
    LEAVE_STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Rejected'),
    )
    
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()
    message = models.TextField()
    status = models.IntegerField(choices=LEAVE_STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff.name} - {self.date}"

    class Meta:
        verbose_name = "Staff Leave"
        verbose_name_plural = "Staff Leaves"
        ordering = ['-created_at']


class Student_Leave(models.Model):
    LEAVE_STATUS_CHOICES = (
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Rejected'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    message = models.TextField()
    status = models.IntegerField(choices=LEAVE_STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.name} - {self.date}"

    class Meta:
        verbose_name = "Student Leave"
        verbose_name_plural = "Student Leaves"
        ordering = ['-created_at']


class StudentFeedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='feedbacks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='feedbacks')
    teacher = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 rating
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.teacher.name}"

    class Meta:
        verbose_name = "Student Feedback"
        verbose_name_plural = "Student Feedbacks"
        ordering = ['-created_at']
        unique_together = ['student', 'subject', 'teacher']  # Prevent duplicate feedbacks


class CourseTracking(models.Model):
    PROGRESS_STATUS_CHOICES = (
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Dropped', 'Dropped'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='course_trackings')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_trackings')
    enrollment_date = models.DateField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    expected_end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    progress_status = models.CharField(max_length=20, choices=PROGRESS_STATUS_CHOICES, default='Not Started')
    completion_percentage = models.IntegerField(default=0, help_text="Percentage of course completion (0-100)")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Course Tracking"
        verbose_name_plural = "Course Trackings"
        unique_together = ['student', 'course']  # Ensure one tracking per student per course
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date and self.expected_end_date and self.start_date > self.expected_end_date:
            raise ValidationError("Start date cannot be after expected end date")
        if self.actual_end_date and self.start_date and self.actual_end_date < self.start_date:
            raise ValidationError("Actual end date cannot be before start date")

    def calculate_completion_percentage(self):
        if not self.start_date or not self.expected_end_date:
            return 0

        today = date.today()

        # If course is completed, return 100%
        if self.progress_status == 'Completed':
            return 100
        elif self.progress_status == 'Dropped':
            return 0

        # Calculate total duration in days
        total_duration = (self.expected_end_date - self.start_date).days
        if total_duration <= 0:
            return 0

        # Calculate elapsed time in days
        elapsed_days = (today - self.start_date).days
        if elapsed_days <= 0:
            return 0

        # Calculate percentage based on course duration type
        if self.course.duration_type == 'Semester':
            # For semester-based courses (6 months)
            max_days = 180  # 6 months = 180 days
            if elapsed_days >= max_days:
                return 100
        else:  # Yearly based
            max_days = 365  # 1 year = 365 days
            if elapsed_days >= max_days:
                return 100

        # Calculate percentage based on elapsed time vs total duration
        percentage = min(100, int((elapsed_days / total_duration) * 100))
        return percentage

    def save(self, *args, **kwargs):
        # Validate dates
        self.clean()
        
        # Calculate completion percentage
        self.completion_percentage = self.calculate_completion_percentage()
        
        # Update progress status based on completion percentage
        if self.completion_percentage >= 100:
            self.progress_status = 'Completed'
            if not self.actual_end_date:
                self.actual_end_date = date.today()
        elif self.completion_percentage > 0:
            self.progress_status = 'In Progress'
        
        super().save(*args, **kwargs)

    @property
    def is_completed(self):
        return self.progress_status == 'Completed'

    @property
    def is_active(self):
        return self.progress_status == 'In Progress'

    @property
    def remaining_days(self):
        if not self.expected_end_date:
            return None
        today = date.today()
        remaining = (self.expected_end_date - today).days
        return max(0, remaining)

    @property
    def duration_type(self):
        return self.course.duration_type

    @property
    def total_duration_days(self):
        if not self.start_date or not self.expected_end_date:
            return None
        return (self.expected_end_date - self.start_date).days

    def get_completion_percentage(self):
        """
        Get completion percentage with caching
        """
        return get_cached_percentage(self.id)

    def force_update_percentage(self):
        """
        Force update the completion percentage and clear cache
        """
        cache_key = f'course_tracking_percentage_{self.id}'
        cache.delete(cache_key)
        self.save()  # This will recalculate and update the percentage


def get_cached_percentage(tracking_id):
    """
    Get cached completion percentage for a course tracking
    """
    cache_key = f'course_tracking_percentage_{tracking_id}'
    percentage = cache.get(cache_key)
    if percentage is None:
        try:
            tracking = CourseTracking.objects.get(id=tracking_id)
            percentage = tracking.completion_percentage
            cache.set(cache_key, percentage, 3600)
        except CourseTracking.DoesNotExist:
            return 0
    return percentage


@receiver(post_save, sender=CourseTracking)
def update_completion_percentage(sender, instance, **kwargs):
    """
    Signal to update completion percentage after save
    Also caches the percentage for 1 hour to avoid frequent recalculations
    """
    cache_key = f'course_tracking_percentage_{instance.id}'
    cache.set(cache_key, instance.completion_percentage, 3600)  # Cache for 1 hour



