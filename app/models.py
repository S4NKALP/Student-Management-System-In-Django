from django.db import models, transaction
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from datetime import date, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .utils import send_push_notification

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
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester_or_year = models.PositiveIntegerField()
    syllabus_pdf = models.FileField(upload_to='subject_pdfs/', null=True, blank=True, help_text="Upload syllabus or study material PDF")

    def __str__(self):
        return f"{self.name} ({self.course.name} - {'Semester' if self.course.duration_type == 'Semester' else 'Year'} {self.semester_or_year})"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate semester/year based on course duration type
        if self.course.duration_type == "Semester":
            max_semesters = self.course.duration * 2
            if self.semester_or_year > max_semesters:
                raise ValidationError(f"Semester cannot exceed {max_semesters}")
        else:  # Year based
            if self.semester_or_year > self.course.duration:
                raise ValidationError(f"Year cannot exceed {self.course.duration}")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_pdf_url(self):
        if self.syllabus_pdf:
            return self.syllabus_pdf.url
        return None

    class Meta:
        unique_together = ['name', 'course', 'semester_or_year']
        ordering = ['course', 'semester_or_year', 'name']


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
        related_name="student_set",
        related_query_name="student",
    )

    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this student belongs to.",
        related_name="students",
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
    marital_status = models.CharField(
        max_length=255, choices=marital_status_choices, null=True, blank=True
    )
    parent_name = models.CharField(max_length=255, null=True, blank=True)
    parent_phone = models.CharField(max_length=255, null=True, blank=True)
    citizenship_no = models.CharField(max_length=255, null=True, blank=True)
    batches = models.ManyToManyField(Batch, related_name="students", blank=True)
    image = models.ImageField(upload_to="student_image", null=True, blank=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )
    current_semester = models.PositiveIntegerField(
        default=1, help_text="Current semester for semester-based courses"
    )
    joining_date = models.DateField(null=True, blank=True)
    password = models.CharField(max_length=128, editable=False, null=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save(update_fields=["password"])

    @property
    def is_staff(self):
        return self.groups.exists()

    def has_perm(self, perm, obj=None):
        if not self.is_active:
            return False

        perms = set()
        for group in self.groups.all():
            perms.update(
                group.permissions.values_list("content_type__app_label", "codename")
            )

        app_label, codename = perm.split(".")
        return (app_label, codename) in perms

    def has_module_perms(self, app_label):
        if not self.is_active:
            return False

        for group in self.groups.all():
            if group.permissions.filter(content_type__app_label=app_label).exists():
                return True
        return False

    def get_current_subjects(self):
        """Get subjects for current semester"""
        if not self.course:
            return Subject.objects.none()
        return Subject.objects.filter(
            course=self.course, semester_or_year=self.current_semester
        )

    def advance_semester(self):
        """Advance to next semester if possible"""
        if not self.course:
            return False

        if self.course.duration_type == "Semester":
            total_semesters = self.course.duration * 2  # 2 semesters per year
            if self.current_semester < total_semesters:
                self.current_semester += 1
                self.save()
                return True
        return False

    def save(self, *args, **kwargs):
        # Remove the course tracking creation from here
        super().save(*args, **kwargs)

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
    parent_name = models.CharField(max_length=255, null=True, blank=True)
    parent_phone = models.CharField(max_length=255, null=True, blank=True)
    citizenship_no = models.CharField(max_length=255, blank=True, null=True)
    passport = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to="staff_image", null=True, blank=True)
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


class Routine(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Staff, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    semester_or_year = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.subject.name} - {self.teacher.name} ({self.start_time} - {self.end_time})"

    class Meta:
        ordering = ['start_time']
        unique_together = ['course', 'subject', 'teacher', 'start_time', 'end_time', 'semester_or_year']


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
        (0, "Pending"),
        (1, "Approved"),
        (2, "Rejected"),
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
        ordering = ["-created_at"]


class Student_Leave(models.Model):
    LEAVE_STATUS_CHOICES = (
        (0, "Pending"),
        (1, "Approved"),
        (2, "Rejected"),
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
        ordering = ["-created_at"]


class StudentFeedback(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="feedbacks"
    )
    teacher = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="feedbacks"
    )
    rating = models.DecimalField(
        max_digits=2, decimal_places=1, choices=[(i / 2, i / 2) for i in range(2, 11)]
    )  # 1 to 5 rating
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.name} - {self.teacher.name}"

    class Meta:
        verbose_name = "Student Feedback"
        verbose_name_plural = "Student Feedbacks"
        ordering = ["-created_at"]
        unique_together = ["student", "teacher"]


class InstituteFeedback(models.Model):
    FEEDBACK_TYPE_CHOICES = (
        ("General", "General"),
        ("Facilities", "Facilities"),
        ("Teaching", "Teaching"),
        ("Infrastructure", "Infrastructure"),
        ("Administration", "Administration"),
    )

    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE, related_name="feedbacks"
    )
    user = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="institute_feedbacks"
    )
    feedback_type = models.CharField(
        max_length=20, choices=FEEDBACK_TYPE_CHOICES, default="General"
    )
    rating = models.DecimalField(
        max_digits=2, decimal_places=1, choices=[(i / 2, i / 2) for i in range(2, 11)]
    )  # 1 to 5 rating
    feedback_text = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.is_anonymous:
            return f"Anonymous - {self.institute.name} - {self.feedback_type}"
        return f"{self.user.name} - {self.institute.name} - {self.feedback_type}"

    class Meta:
        verbose_name = "Student Institute Feedback"
        verbose_name_plural = "Student Institute Feedbacks"
        ordering = ["-created_at"]
        unique_together = [
            "user",
            "institute",
            "feedback_type",
        ]  # One feedback per type per user

    @property
    def display_name(self):
        """Return anonymous if feedback is anonymous, otherwise return user's name"""
        return "Anonymous" if self.is_anonymous else self.user.name


class StaffInstituteFeedback(models.Model):
    """Model for tracking feedback from staff members to the institute"""
    FEEDBACK_TYPE_CHOICES = (
        ("General", "General"),
        ("Facilities", "Facilities"),
        ("Teaching", "Teaching"),
        ("Infrastructure", "Infrastructure"),
        ("Administration", "Administration"),
    )

    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE, related_name="staff_feedbacks"
    )
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="institute_feedbacks"
    )
    feedback_type = models.CharField(
        max_length=20, choices=FEEDBACK_TYPE_CHOICES, default="General"
    )
    rating = models.DecimalField(
        max_digits=2, decimal_places=1, choices=[(i / 2, i / 2) for i in range(2, 11)]
    )  # 1 to 5 rating
    feedback_text = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.is_anonymous:
            return f"Anonymous - {self.institute.name} - {self.feedback_type}"
        return f"{self.staff.name} - {self.institute.name} - {self.feedback_type}"

    class Meta:
        verbose_name = "Staff Institute Feedback"
        verbose_name_plural = "Staff Institute Feedbacks"
        ordering = ["-created_at"]
        unique_together = [
            "staff",
            "institute",
            "feedback_type",
        ]  # One feedback per type per staff

    @property
    def display_name(self):
        """Return anonymous if feedback is anonymous, otherwise return staff's name"""
        return "Anonymous" if self.is_anonymous else self.staff.name


class CourseTracking(models.Model):
    PROGRESS_STATUS_CHOICES = (
        ("Not Started", "Not Started"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
        ("Dropped", "Dropped"),
    )

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="course_trackings"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="student_trackings"
    )
    enrollment_date = models.DateField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    expected_end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    progress_status = models.CharField(
        max_length=20, choices=PROGRESS_STATUS_CHOICES, default="Not Started"
    )
    completion_percentage = models.IntegerField(
        default=0, help_text="Percentage of course completion (0-100)"
    )
    current_semester = models.PositiveIntegerField(default=1)
    semester_start_date = models.DateField(null=True, blank=True)
    semester_end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Course Tracking"
        verbose_name_plural = "Course Trackings"
        unique_together = ["student", "course"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.student or not self.course:
            raise ValidationError("Both student and course are required")

        if self.start_date and self.expected_end_date and self.start_date > self.expected_end_date:
            raise ValidationError("Start date cannot be after expected end date")
        
        if self.actual_end_date and self.start_date and self.actual_end_date < self.start_date:
            raise ValidationError("Actual end date cannot be before start date")
        
        if self.semester_start_date and self.semester_end_date and self.semester_start_date > self.semester_end_date:
            raise ValidationError("Semester start date cannot be after semester end date")
        
        if self.current_semester < 1:
            raise ValidationError("Current semester must be at least 1")
        
        if self.course.duration_type == "Semester":
            max_semesters = self.course.duration * 2
            if self.current_semester > max_semesters:
                raise ValidationError(f"Current semester cannot exceed {max_semesters}")

    def calculate_completion_percentage(self):
        if not self.start_date or not self.expected_end_date:
            return 0

        today = date.today()

        # If course is completed, return 100%
        if self.progress_status == "Completed":
            return 100
        elif self.progress_status == "Dropped":
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
        if self.course.duration_type == "Semester":
            # For semester-based courses
            semester_duration = 180  # 6 months = 180 days
            total_semesters = self.course.duration * 2  # 2 semesters per year
            completed_semesters = self.current_semester - 1
            semester_progress = (completed_semesters / total_semesters) * 100

            # If current semester is completed
            if self.semester_end_date and today > self.semester_end_date:
                semester_progress = (self.current_semester / total_semesters) * 100

            return min(100, int(semester_progress))
        else:  # Yearly based
            max_days = 365  # 1 year = 365 days
            if elapsed_days >= max_days:
                return 100

        # Calculate percentage based on elapsed time vs total duration
        percentage = min(100, int((elapsed_days / total_duration) * 100))
        return percentage

    def save(self, *args, **kwargs):
        # Calculate dates if this is a new instance
        if not self.pk:
            self.start_date = self.start_date or date.today()
            
            # Calculate expected end date based on course duration
            if self.course.duration_type == "Year":
                years = self.course.duration
            else:  # Semester based
                years = self.course.duration  # Duration is already in years
            
            self.expected_end_date = self.start_date + timedelta(days=years * 365)
            
            # Set initial semester dates
            self.semester_start_date = self.start_date
            self.semester_end_date = self.start_date + timedelta(days=180)  # 6 months

        # Validate dates and other fields
        self.clean()

        # Calculate completion percentage
        self.completion_percentage = self.calculate_completion_percentage()

        # Update progress status based on completion percentage
        if self.completion_percentage >= 100:
            self.progress_status = "Completed"
            if not self.actual_end_date:
                self.actual_end_date = date.today()
        elif self.completion_percentage > 0:
            self.progress_status = "In Progress"

        try:
            super().save(*args, **kwargs)
        except Exception as e:
            print(f"Error saving course tracking for {self.student.name}: {str(e)}")
            raise

    def advance_semester(self):
        """Advance to next semester if possible"""
        if not self.course or self.course.duration_type != "Semester":
            return False

        total_semesters = self.course.duration * 2
        if self.current_semester < total_semesters:
            self.current_semester += 1
            self.semester_start_date = date.today()
            self.semester_end_date = self.semester_start_date + timedelta(
                days=180
            )  # 6 months
            # Update student's current semester as well
            self.student.current_semester = self.current_semester
            self.student.save()
            self.save()
            return True
        return False

    @property
    def is_completed(self):
        return self.progress_status == "Completed"

    @property
    def is_active(self):
        return self.progress_status == "In Progress"

    @property
    def remaining_days(self):
        """Returns remaining days in current semester"""
        if not self.semester_end_date:
            return None
        today = date.today()
        remaining = (self.semester_end_date - today).days
        return max(0, remaining)

    @property
    def total_remaining_days(self):
        """Returns remaining days for entire course"""
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
        return get_cached_percentage(self.id)

    def force_update_percentage(self):
        cache_key = f"course_tracking_percentage_{self.id}"
        cache.delete(cache_key)
        self.save()


def get_cached_percentage(tracking_id):
    """
    Get cached completion percentage for a course tracking
    """
    cache_key = f"course_tracking_percentage_{tracking_id}"
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
    cache_key = f"course_tracking_percentage_{instance.id}"
    cache.set(cache_key, instance.completion_percentage, 3600)  # Cache for 1 hour


@receiver(post_save, sender=Student)
def create_course_tracking(sender, instance, created, **kwargs):
    """
    Signal handler to create CourseTracking when a new student is created
    or when a course is assigned to an existing student
    """
    print(f"Signal triggered for student: {instance.name}")
    print(f"Created: {created}")
    print(f"Course: {instance.course}")
    print(f"Current Semester: {instance.current_semester}")

    # Check if student has a course assigned
    if instance.course:
        try:
            # Check if course tracking already exists
            existing_tracking = CourseTracking.objects.filter(
                student=instance,
                course=instance.course
            ).first()

            if existing_tracking:
                print(f"Course tracking already exists for {instance.name}")
                return

            # Calculate dates based on course duration
            start_date = instance.joining_date or date.today()
            
            # Calculate expected end date based on course duration type
            if instance.course.duration_type == "Year":
                # For year-based courses, each year is 365 days
                years = instance.course.duration
                duration_days = years * 365
            else:  # Semester based
                # For semester-based courses:
                # - Each year has 2 semesters
                # - Total years is the same as course duration
                years = instance.course.duration
                duration_days = years * 365  # Use full years for total duration
            
            expected_end_date = start_date + timedelta(days=duration_days)
            
            # Create course tracking with transaction
            with transaction.atomic():
                course_tracking = CourseTracking.objects.create(
                    student=instance,
                    course=instance.course,
                    start_date=start_date,
                    expected_end_date=expected_end_date,
                    current_semester=instance.current_semester,
                    semester_start_date=start_date,
                    semester_end_date=start_date + timedelta(days=180)  # 6 months for first semester
                )
                
                # Force initial percentage calculation
                course_tracking.force_update_percentage()
                
                print(f"Successfully created course tracking for student {instance.name}")
                print(f"Start Date: {start_date}")
                print(f"Expected End Date: {expected_end_date}")
                print(f"Current Semester: {instance.current_semester}")
                
        except Exception as e:
            print(f"Error creating course tracking for student {instance.name}: {str(e)}")
            # Log the error but don't prevent student creation
            # You might want to add proper logging here instead of print statements
    else:
        print(f"No course assigned to student {instance.name}")


@receiver(post_save, sender=Student)
def sync_student_semester(sender, instance, created, **kwargs):
    """Signal handler to sync student's current_semester with course tracking"""
    if instance.course:
        try:
            course_tracking = CourseTracking.objects.get(student=instance, course=instance.course)
            if course_tracking.current_semester != instance.current_semester:
                course_tracking.current_semester = instance.current_semester
                course_tracking.save()
        except CourseTracking.DoesNotExist:
            pass


@receiver(post_save, sender=CourseTracking)
def sync_course_tracking_semester(sender, instance, created, **kwargs):
    """Signal handler to sync course tracking's current_semester with student"""
    if instance.student.current_semester != instance.current_semester:
        instance.student.current_semester = instance.current_semester
        instance.student.save()
