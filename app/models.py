# Standard library imports
from datetime import date, timedelta, datetime

# Core Django imports
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# Third-party app imports
from model_utils import FieldTracker

# Local app imports
from app.firebase import send_push_notification, FCMDevice

# Constants
DURATION_TYPES = (
    ("Year", "Year Based"),
    ("Semester", "Semester Based"),
)

STUDENT_STATUS_CHOICES = (
    ("Active", "Active"),
    ("Leave", "Leave"),
    ("Completed", "Completed"),
)

GENDER_CHOICES = (
    ("Male", "Male"),
    ("Female", "Female"),
    ("Other", "Other"),
)

MARITAL_STATUS_CHOICES = (
    ("Married", "Married"),
    ("Unmarried", "Unmarried"),
    ("Divorced", "Divorced"),
)

LEAVE_STATUS_CHOICES = (
    (0, "Pending"),
    (1, "Approved"),
    (2, "Rejected"),
)

FEEDBACK_TYPE_CHOICES = (
    ("General", "General"),
    ("Facilities", "Facilities"),
    ("Teaching", "Teaching"),
    ("Infrastructure", "Infrastructure"),
    ("Administration", "Administration"),
)

PROGRESS_STATUS_CHOICES = (
    ("Not Started", "Not Started"),
    ("In Progress", "In Progress"),
    ("Completed", "Completed"),
    ("Dropped", "Dropped"),
)


# Base Models
class Institute(models.Model):
    """Model representing an educational institute"""

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


# Academic Models
class Batch(models.Model):
    """Model representing a batch of students"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    year = models.DateField(
        null=True, blank=True, help_text="Starting date for all students in this batch"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Batch"
        verbose_name_plural = "Batches"


# Course Related Models
class Course(models.Model):
    """Model representing a course offered by the institute"""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=500)
    code = models.CharField(max_length=20, null=True, blank=True)
    duration = models.IntegerField(default=1, null=True, blank=True)
    duration_type = models.CharField(
        max_length=255, choices=DURATION_TYPES, null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"


class Subject(models.Model):
    """Model representing a subject within a course"""

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    period_or_year = models.PositiveIntegerField(
        help_text="Period number (semester or year) for this subject"
    )
    syllabus_pdf = models.FileField(
        upload_to="subject_pdfs/",
        null=True,
        blank=True,
        help_text="Upload syllabus or study material PDF",
    )

    def __str__(self):
        return f"{self.name} ({self.course.name} - {'Semester' if self.course.duration_type == 'Semester' else 'Year'} {self.period_or_year})"

    def clean(self):
        if self.course.duration_type == "Semester":
            max_periods = self.course.duration * 2
            if self.period_or_year > max_periods:
                raise ValidationError(f"Period cannot exceed {max_periods} semesters")
        else:  # Year based
            if self.period_or_year > self.course.duration:
                raise ValidationError(
                    f"Period cannot exceed {self.course.duration} years"
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_pdf_url(self):
        return self.syllabus_pdf.url if self.syllabus_pdf else None

    def get_all_files(self):
        """Get all files associated with this subject including syllabus and additional files"""
        files = []
        if self.syllabus_pdf:
            files.append(
                {
                    "id": "syllabus",
                    "title": f"{self.name} Syllabus",
                    "description": f"Syllabus PDF for {self.name}",
                    "file_url": self.syllabus_pdf.url,
                    "file_type": "syllabus",
                    "uploaded_by": None,
                    "uploaded_at": None,
                }
            )

        subject_files = self.subjectfile_set.all().order_by("-uploaded_at")
        for file in subject_files:
            files.append(
                {
                    "id": file.id,
                    "title": file.title,
                    "description": file.description,
                    "file_url": file.file.url,
                    "file_type": "notes",
                    "uploaded_by": file.uploaded_by.name if file.uploaded_by else None,
                    "uploaded_at": file.uploaded_at,
                }
            )

        return files

    class Meta:
        unique_together = ["name", "course", "period_or_year"]
        ordering = ["course", "period_or_year", "name"]


class SubjectFile(models.Model):
    """Model to store additional files for subjects (notes, study materials, etc.)"""

    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to="subject_files/")
    uploaded_by = models.ForeignKey("Staff", on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

    class Meta:
        ordering = ["-uploaded_at"]


# User Models
class Student(AbstractUser):
    """Model representing a student in the institute"""

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
        max_length=255, choices=STUDENT_STATUS_CHOICES, null=True, blank=True
    )
    gender = models.CharField(
        max_length=255, choices=GENDER_CHOICES, null=True, blank=True
    )
    birth_date = models.DateField(null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True, unique=True)
    temporary_address = models.CharField(max_length=500, null=True, blank=True)
    permanent_address = models.CharField(max_length=500, null=True, blank=True)
    marital_status = models.CharField(
        max_length=255, choices=MARITAL_STATUS_CHOICES, null=True, blank=True
    )
    parent_name = models.CharField(max_length=255, null=True, blank=True)
    parent_phone = models.CharField(max_length=255, null=True, blank=True)
    citizenship_no = models.CharField(max_length=255, null=True, blank=True)
    batches = models.ManyToManyField("Batch", related_name="students", blank=True)
    image = models.ImageField(upload_to="student_image", null=True, blank=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )
    current_period = models.PositiveIntegerField(
        default=1, help_text="Current semester/year for the student's course"
    )
    joining_date = models.DateField(null=True, blank=True)
    password = models.CharField(max_length=128, editable=False, null=True)
    fcm_token = models.CharField(max_length=500, null=True, blank=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        """Set the password for the student"""
        if raw_password:
            self.password = make_password(raw_password)
            if self.pk:  # Only use update_fields if the object has a primary key
                self.save(update_fields=["password"])
            else:
                self.save()
        else:
            self.password = None
            if self.pk:  # Only use update_fields if the object has a primary key
                self.save(update_fields=["password"])
            else:
                self.save()

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
        """Get subjects for current period"""
        if not self.course:
            return Subject.objects.none()
        return Subject.objects.filter(
            course=self.course, period_or_year=self.current_period
        )

    def advance_period(self):
        """Advance to next period if possible"""
        if not self.course:
            return False

        if self.course.duration_type == "Semester":
            total_periods = self.course.duration * 2
            if self.current_period < total_periods:
                self.current_period += 1
                self.save()
                return True
        else:  # Year based
            if self.current_period < self.course.duration:
                self.current_period += 1
                self.save()
                return True
        return False

    def save(self, *args, **kwargs):
        # Call the original save method to ensure the student is saved
        super().save(*args, **kwargs)

        # After saving, check if we need to sync joining date with batch
        if hasattr(self, "_batch_to_sync"):
            batch = self._batch_to_sync
            if batch and batch.year and not self.joining_date:
                self.joining_date = batch.year
                super().save(update_fields=["joining_date"])
            delattr(self, "_batch_to_sync")

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"


class Staff(AbstractUser):
    """Model representing staff members of the institute"""

    first_name = None
    last_name = None
    date_joined = None
    username = None
    email = None
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this staff.",
        related_name="staff_set",
        related_query_name="staff",
    )

    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this staff belongs to.",
        related_name="staffs",
    )

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, null=True, blank=True, unique=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(
        max_length=255, choices=GENDER_CHOICES, null=True, blank=True
    )
    birth_date = models.DateField(null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    temporary_address = models.CharField(max_length=255, null=True, blank=True)
    permanent_address = models.CharField(max_length=255, null=True, blank=True)
    marital_status = models.CharField(
        max_length=255, choices=MARITAL_STATUS_CHOICES, null=True, blank=True
    )
    parent_name = models.CharField(max_length=255, null=True, blank=True)
    parent_phone = models.CharField(max_length=255, null=True, blank=True)
    citizenship_no = models.CharField(max_length=255, blank=True, null=True)
    passport = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to="staff_image", null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    password = models.CharField(max_length=128, editable=False, null=True)
    fcm_token = models.CharField(max_length=500, null=True, blank=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hod",
        help_text="Course for which this staff member is HOD",
    )

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        """Set the password for the staff"""
        if raw_password:
            self.password = make_password(raw_password)
            self.save(update_fields=["password"])
        else:
            self.password = None
            self.save(update_fields=["password"])

    def check_password(self, raw_password):
        """Check if the given password matches the stored password hash"""
        if not self.password:
            return False
        return check_password(raw_password, self.password)

    @property
    def is_staff(self):
        return (
            self.groups.filter(name__in=["Teacher", "Admission Officer"]).exists()
            or self.is_superuser
        )

    @property
    def is_authenticated(self):
        return True

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

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staffs"


class Routine(models.Model):
    """Model representing class routine"""

    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Staff, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    period_or_year = models.PositiveIntegerField(
        help_text="Period number (semester or year) for this routine"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.subject.name} - {self.teacher.name} ({self.start_time} - {self.end_time})"

    class Meta:
        ordering = ["start_time"]
        unique_together = [
            "course",
            "subject",
            "teacher",
            "start_time",
            "end_time",
            "period_or_year",
        ]


# Attendance Models
class Attendance(models.Model):
    """Model representing attendance records"""

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
    """Model representing individual student attendance records"""

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


# Notice Model
class Notice(models.Model):
    """Model representing notices/announcements"""

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="notice", blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Notice"
        verbose_name_plural = "Notices"


# Leave Models
class StaffLeave(models.Model):
    """Model representing staff leave requests"""

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    message = models.TextField()
    status = models.IntegerField(choices=LEAVE_STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff.name} - {self.start_date} to {self.end_date}"

    class Meta:
        verbose_name = "Staff Leave"
        verbose_name_plural = "Staff Leaves"
        ordering = ["-created_at"]


class StudentLeave(models.Model):
    """Model representing student leave requests"""

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="leave_requests"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    message = models.TextField()
    status = models.IntegerField(choices=LEAVE_STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.name} - {self.start_date} to {self.end_date}"

    class Meta:
        verbose_name = "Student Leave"
        verbose_name_plural = "Student Leaves"
        ordering = ["-created_at"]


# Feedback Models
class StudentFeedback(models.Model):
    """Model representing student feedback for teachers"""

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="feedbacks"
    )
    teacher = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="feedbacks"
    )
    rating = models.DecimalField(
        max_digits=2, decimal_places=1, choices=[(i / 2, i / 2) for i in range(2, 11)]
    )
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


class ParentFeedback(models.Model):
    """Model representing feedback from parents about teachers"""

    parent = models.ForeignKey(
        "Parent", on_delete=models.CASCADE, related_name="feedbacks"
    )
    teacher = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="parent_feedbacks"
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="parent_feedbacks"
    )
    rating = models.DecimalField(
        max_digits=2, decimal_places=1, choices=[(i / 2, i / 2) for i in range(2, 11)]
    )
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.parent.name} - {self.teacher.name} - {self.student.name}"

    class Meta:
        verbose_name = "Parent Feedback"
        verbose_name_plural = "Parent Feedbacks"
        ordering = ["-created_at"]
        unique_together = ["parent", "teacher", "student"]


class InstituteFeedback(models.Model):
    """Model representing student feedback for the institute"""

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
    )
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
        unique_together = ["user", "institute", "feedback_type"]

    @property
    def display_name(self):
        return "Anonymous" if self.is_anonymous else self.user.name


class StaffInstituteFeedback(models.Model):
    """Model representing staff feedback for the institute"""

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
    )
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
        unique_together = ["staff", "institute", "feedback_type"]

    @property
    def display_name(self):
        return "Anonymous" if self.is_anonymous else self.staff.name


class ParentInstituteFeedback(models.Model):
    """Model representing parent feedback for the institute"""

    institute = models.ForeignKey(
        Institute, on_delete=models.CASCADE, related_name="parent_feedbacks"
    )
    parent = models.ForeignKey(
        "Parent", on_delete=models.CASCADE, related_name="institute_feedbacks"
    )
    feedback_type = models.CharField(
        max_length=20, choices=FEEDBACK_TYPE_CHOICES, default="General"
    )
    rating = models.DecimalField(
        max_digits=2, decimal_places=1, choices=[(i / 2, i / 2) for i in range(2, 11)]
    )
    feedback_text = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.is_anonymous:
            return f"Anonymous - {self.institute.name} - {self.feedback_type}"
        return f"{self.parent.name} - {self.institute.name} - {self.feedback_type}"

    class Meta:
        verbose_name = "Parent Institute Feedback"
        verbose_name_plural = "Parent Institute Feedbacks"
        ordering = ["-created_at"]
        unique_together = ["parent", "institute", "feedback_type"]

    @property
    def display_name(self):
        return "Anonymous" if self.is_anonymous else self.parent.name


# Course Tracking Model
class CourseTracking(models.Model):
    """Model for tracking student progress in courses"""

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
        max_length=20, choices=PROGRESS_STATUS_CHOICES, default="In Progress"
    )
    completion_percentage = models.IntegerField(
        default=0, help_text="Percentage of course completion (0-100)"
    )
    current_period = models.PositiveIntegerField(
        default=1, help_text="Current semester/year depending on course duration type"
    )
    period_start_date = models.DateField(
        null=True, blank=True, help_text="Start date of current semester/year"
    )
    period_end_date = models.DateField(
        null=True, blank=True, help_text="End date of current semester/year"
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"

    def clean(self):
        if not self.student or not self.course:
            raise ValidationError("Both student and course are required")

        if (
            self.start_date
            and self.expected_end_date
            and self.start_date > self.expected_end_date
        ):
            raise ValidationError("Start date cannot be after expected end date")

        if (
            self.actual_end_date
            and self.start_date
            and self.actual_end_date < self.start_date
        ):
            raise ValidationError("Actual end date cannot be before start date")

        if (
            self.period_start_date
            and self.period_end_date
            and self.period_start_date > self.period_end_date
        ):
            raise ValidationError("Period start date cannot be after period end date")

        if self.current_period < 1:
            raise ValidationError("Current period must be at least 1")

        if self.course.duration_type == "Semester":
            max_periods = self.course.duration * 2
            if self.current_period > max_periods:
                raise ValidationError(f"Current semester cannot exceed {max_periods}")
        else:  # Year based
            if self.current_period > self.course.duration:
                raise ValidationError(
                    f"Current year cannot exceed {self.course.duration}"
                )

    def calculate_completion_percentage(self):
        if not self.start_date or not self.expected_end_date:
            return 0

        today = date.today()

        if self.progress_status == "Completed":
            return 100
        elif self.progress_status == "Dropped":
            return 0

        total_duration = (self.expected_end_date - self.start_date).days
        if total_duration <= 0:
            return 0

        elapsed_days = (today - self.start_date).days
        if elapsed_days <= 0:
            return 0

        if self.course.duration_type == "Semester":
            total_periods = self.course.duration * 2
            completed_periods = self.current_period - 1
            period_progress = (completed_periods / total_periods) * 100

            if self.period_end_date and today > self.period_end_date:
                period_progress = (self.current_period / total_periods) * 100

            return min(100, int(period_progress))
        else:  # Year based
            total_periods = self.course.duration
            completed_periods = self.current_period - 1
            period_progress = (completed_periods / total_periods) * 100

            if self.period_end_date and today > self.period_end_date:
                period_progress = (self.current_period / total_periods) * 100

            return min(100, int(period_progress))

    def get_completion_percentage(self):
        return self.completion_percentage

    def update_completion_percentage(self):
        new_percentage = self.calculate_completion_percentage()
        if new_percentage != self.completion_percentage:
            self.completion_percentage = new_percentage
            self.save(update_fields=["completion_percentage"])
        return new_percentage

    def force_update_percentage(self):
        return self.update_completion_percentage()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.start_date = self.start_date or date.today()

            if self.course.duration_type == "Year":
                years = self.course.duration
            else:  # Semester based
                years = self.course.duration

            self.expected_end_date = self.start_date + timedelta(days=years * 365)

            # Set period dates based on duration type
            self.period_start_date = self.start_date
            if self.course.duration_type == "Semester":
                self.period_end_date = self.start_date + timedelta(days=180)  # 6 months
            else:
                self.period_end_date = self.start_date + timedelta(days=365)  # 1 year

        self.clean()
        self.completion_percentage = self.calculate_completion_percentage()

        # Check if course duration has been completed
        today = date.today()
        if self.expected_end_date and today >= self.expected_end_date:
            self.progress_status = "Completed"
            if not self.actual_end_date:
                self.actual_end_date = today
        elif self.completion_percentage >= 100:
            self.progress_status = "Completed"
            if not self.actual_end_date:
                self.actual_end_date = today
        elif self.completion_percentage > 0:
            self.progress_status = "In Progress"

        try:
            super().save(*args, **kwargs)
        except Exception as e:
            print(f"Error saving course tracking for {self.student.name}: {str(e)}")
            raise

    def advance_period(self):
        """Advance to next semester/year based on course duration type"""
        if not self.course:
            return False

        if self.course.duration_type == "Semester":
            total_periods = self.course.duration * 2
            if self.current_period < total_periods:
                self.current_period += 1
                # Update period dates
                self.period_start_date = self.period_end_date
                self.period_end_date = self.period_start_date + timedelta(days=180)
                self.save()
                return True
        else:  # Year based
            if self.current_period < self.course.duration:
                self.current_period += 1
                # Update period dates
                self.period_start_date = self.period_end_date
                self.period_end_date = self.period_start_date + timedelta(days=365)
                self.save()
                return True
        return False

    @property
    def is_completed(self):
        return self.progress_status == "Completed"

    @property
    def is_active(self):
        return self.progress_status in ["Not Started", "In Progress"]

    @property
    def remaining_days(self):
        """Get remaining days in current period (semester/year)"""
        if not self.period_end_date:
            return 0
        return max(0, (self.period_end_date - date.today()).days)

    @property
    def total_remaining_days(self):
        """Get total remaining days in course"""
        if not self.expected_end_date:
            return 0
        return max(0, (self.expected_end_date - date.today()).days)

    @property
    def duration_type(self):
        return self.course.duration_type if self.course else None

    @property
    def total_duration_days(self):
        if not self.start_date or not self.expected_end_date:
            return 0
        return (self.expected_end_date - self.start_date).days

    @property
    def current_period_display(self):
        """Display current period as semester or year based on course type"""
        if not self.course:
            return "N/A"
        return f"{'Semester' if self.course.duration_type == 'Semester' else 'Year'} {self.current_period}"

    class Meta:
        verbose_name = "Course Tracking"
        verbose_name_plural = "Course Trackings"
        unique_together = ["student", "course"]
        ordering = ["-created_at"]


# Authentication Models
class TOTPSecret(models.Model):
    """Model to store TOTP secret keys"""

    identifier = models.CharField(max_length=255)  # phone or email
    secret_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["identifier"]),
            models.Index(fields=["expires_at"]),
        ]

    def is_expired(self):
        return timezone.now() > self.expires_at


class ResetToken(models.Model):
    """Model to store password reset tokens"""

    token = models.UUIDField(unique=True)
    identifier = models.CharField(max_length=255)  # phone or email
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["expires_at"]),
        ]

    def is_expired(self):
        return timezone.now() > self.expires_at


class Parent(AbstractUser):
    """Model representing a parent of a student"""

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
        help_text="Specific permissions for this parent.",
        related_name="parent_set",
        related_query_name="parent",
    )

    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this parent belongs to.",
        related_name="parents",
    )

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    students = models.ManyToManyField(Student, related_name="parents")
    password = models.CharField(max_length=128, editable=False, null=True)
    fcm_token = models.CharField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to="parent_images/", null=True, blank=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save(update_fields=["password"])

    @property
    def is_staff(self):
        return False

    def has_perm(self, perm, obj=None):
        if not self.is_active:
            return False

        # Check if parent has the permission through their groups
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

        # Check if parent has any permissions for the app through their groups
        for group in self.groups.all():
            if group.permissions.filter(content_type__app_label=app_label).exists():
                return True
        return False

    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents"


class TeacherParentMeeting(models.Model):
    """Model for teacher-parent meetings"""

    MEETING_STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("rescheduled", "Rescheduled"),
    ]
    meeting_date = models.DateField()
    meeting_time = models.TimeField()
    duration = models.IntegerField(help_text="Duration in minutes", default=30)
    status = models.CharField(
        max_length=20, choices=MEETING_STATUS_CHOICES, default="scheduled"
    )
    agenda = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancellation_reason = models.TextField(blank=True)
    meeting_link = models.URLField(blank=True, help_text="For online meetings")
    is_online = models.BooleanField(default=False)

    # Add tracker for change detection in signals
    tracker = FieldTracker(fields=["status"])

    class Meta:
        ordering = ["-meeting_date", "-meeting_time"]
        unique_together = ["meeting_date", "meeting_time"]

    def __str__(self):
        return f"Meeting on {self.meeting_date}"

    def save(self, *args, **kwargs):
        # Only keep validation logic, notification is handled by signals
        # Check for overlapping meetings
        if self.status == "scheduled":
            overlapping = TeacherParentMeeting.objects.filter(
                meeting_date=self.meeting_date, status="scheduled"
            ).exclude(id=self.id)

            for meeting in overlapping:
                # Convert times to datetime for comparison
                meeting_start = datetime.combine(
                    meeting.meeting_date, meeting.meeting_time
                )
                meeting_end = meeting_start + timedelta(minutes=meeting.duration)
                new_start = datetime.combine(self.meeting_date, self.meeting_time)
                new_end = new_start + timedelta(minutes=self.duration)

                if new_start < meeting_end and new_end > meeting_start:
                    raise ValidationError(
                        "This time slot overlaps with another meeting"
                    )

        # Save the meeting
        super().save(*args, **kwargs)

    def get_status_display(self):
        return dict(self.MEETING_STATUS_CHOICES)[self.status]

    def is_upcoming(self):
        now = timezone.now()
        meeting_datetime = timezone.make_aware(
            datetime.combine(self.meeting_date, self.meeting_time)
        )
        return meeting_datetime > now and self.status == "scheduled"

    def is_past(self):
        now = timezone.now()
        meeting_datetime = timezone.make_aware(
            datetime.combine(self.meeting_date, self.meeting_time)
        )
        return meeting_datetime < now

    def can_be_cancelled(self):
        return self.status == "scheduled" and self.is_upcoming()

    def can_be_rescheduled(self):
        return self.status in ["scheduled", "rescheduled"] and self.is_upcoming()
