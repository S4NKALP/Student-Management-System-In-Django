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
from django.conf import settings

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
    batches = models.ManyToManyField("Batch", related_name="courses", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['duration_type']),
            models.Index(fields=['name', 'is_active']),  # For active course lookups
            models.Index(fields=['code', 'is_active']),  # For active course lookups by code
        ]

    def cleanup_orphaned_data(self):
        """
        Clean up orphaned data related to this course
        """
        # Clean up subjects using the correct reverse relationship
        Subject.objects.filter(course=self).delete()
        
        # Clean up course tracking records
        self.student_trackings.all().delete()
        
        # Clean up routine records
        self.routines.all().delete()


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
        indexes = [
            models.Index(fields=['course']),
            models.Index(fields=['period_or_year']),
            models.Index(fields=['name']),
            models.Index(fields=['course', 'period_or_year']),  # For course period subjects
            models.Index(fields=['name', 'course']),            # For subject lookups
        ]

    def cleanup_orphaned_data(self):
        """
        Clean up orphaned data related to this subject
        """
        # Clean up subject files
        self.subjectfile_set.all().delete()
        
        # Clean up routine records
        self.routines.all().delete()
        
        # Clean up attendance records
        self.attendance_records.all().delete()


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
        try:
            with transaction.atomic():
                # Validate data before saving
                self.full_clean()
                
                # Call the original save method
                super().save(*args, **kwargs)
                
                # Update related records in the same transaction
                if hasattr(self, 'course_trackings'):
                    for tracking in self.course_trackings.all():
                        tracking.update_completion_percentage()
        except ValidationError as e:
            raise ValidationError(f"Validation error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error saving student: {str(e)}")

    def clean(self):
        """Validate student data before saving"""
        if self.phone and not self.phone.isdigit():
            raise ValidationError("Phone number must contain only digits")
        
        if self.email and '@' not in self.email:
            raise ValidationError("Invalid email format")
        
        if self.birth_date and self.birth_date > date.today():
            raise ValidationError("Birth date cannot be in the future")
        
        if self.joining_date and self.joining_date > date.today():
            raise ValidationError("Joining date cannot be in the future")

    def cleanup_orphaned_data(self):
        """
        Clean up orphaned data related to this student
        """
        # Clean up attendance records
        self.attendance_records.all().delete()
        
        # Clean up course tracking
        self.course_trackings.all().delete()
        
        # Clean up leave records
        self.leave_requests.all().delete()
        
        # Clean up meeting records
        self.meetings.clear()

    def validate_data(self):
        """
        Validate student data before saving
        """
        if not self.name:
            raise ValidationError("Student name is required")
        if not self.phone:
            raise ValidationError("Student phone number is required")
        if not self.gender:
            raise ValidationError("Student gender is required")
        if not self.birth_date:
            raise ValidationError("Student birth date is required")

    def get_notification_tokens(self):
        """
        Get FCM tokens for notifications
        """
        tokens = set()
        
        # Get student's token
        if self.fcm_token:
            tokens.add(self.fcm_token)
            
        # Get parent's token
        if self.parent and self.parent.fcm_token:
            tokens.add(self.parent.fcm_token)
            
        return tokens

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['status']),
            models.Index(fields=['course']),
            models.Index(fields=['current_period']),
            models.Index(fields=['joining_date']),
        ]


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
    courses_taught = models.ManyToManyField(Course, related_name="teachers", blank=True)
    meetings = models.ManyToManyField("TeacherParentMeeting", related_name="staff_members", blank=True)

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

    def clean(self):
        """Validate staff data before saving"""
        if self.phone and not self.phone.isdigit():
            raise ValidationError("Phone number must contain only digits")
        
        if self.email and '@' not in self.email:
            raise ValidationError("Invalid email format")
        
        if self.birth_date and self.birth_date > date.today():
            raise ValidationError("Birth date cannot be in the future")
        
        if self.joining_date and self.joining_date > date.today():
            raise ValidationError("Joining date cannot be in the future")

    def cleanup_orphaned_data(self):
        """
        Clean up orphaned data related to this staff member
        """
        # Clean up attendance records
        self.attendance_records.all().delete()
        
        # Clean up course assignments
        self.courses_taught.clear()
        
        # Clean up meeting records
        self.meetings.clear()

    def validate_data(self):
        """
        Validate staff data before saving
        """
        if not self.name:
            raise ValidationError("Staff name is required")
        if not self.phone:
            raise ValidationError("Staff phone number is required")
        if not self.gender:
            raise ValidationError("Staff gender is required")
        if not self.designation:
            raise ValidationError("Staff designation is required")

    def get_notification_tokens(self):
        """
        Get FCM tokens for notifications
        """
        tokens = set()
        
        # Get staff's token
        if self.fcm_token:
            tokens.add(self.fcm_token)
            
        return tokens

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staffs"
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['designation']),
            models.Index(fields=['is_active']),
            models.Index(fields=['course']),
            # Add these composite indexes
            models.Index(fields=['designation', 'is_active']),  # For active staff by role
            models.Index(fields=['course', 'is_active']),       # For course staff
            models.Index(fields=['phone', 'is_active']),        # For active staff lookups
        ]


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
        indexes = [
            models.Index(fields=['course']),
            models.Index(fields=['subject']),
            models.Index(fields=['teacher']),
            models.Index(fields=['is_active']),
            models.Index(fields=['period_or_year']),
            models.Index(fields=['course', 'period_or_year']),  # For course routines
            models.Index(fields=['teacher', 'is_active']),      # For teacher schedules
            models.Index(fields=['subject', 'is_active']),      # For subject schedules
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
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['routine']),
            models.Index(fields=['teacher']),
            models.Index(fields=['class_status']),
            # Add these composite indexes
            models.Index(fields=['date', 'routine']),           # For date-based routine lookups
            models.Index(fields=['teacher', 'date']),           # For teacher attendance history
            models.Index(fields=['routine', 'class_status']),   # For class status filtering
        ]


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

    class Meta:
        indexes = [
            models.Index(fields=['attendance']),
            models.Index(fields=['student']),
            models.Index(fields=['student_attend']),
            # Add these composite indexes
            models.Index(fields=['student', 'student_attend']),  # For attendance filtering
            models.Index(fields=['attendance', 'student']),      # For attendance lookups
            models.Index(fields=['attendance', 'student_attend']), # For attendance status
        ]


# Notice Model
class Notice(models.Model):
    """Model representing notices/announcements"""

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="notice", blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="notice_file", blank=True, null=True)
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
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['student', 'status']),         # For student leave status
            models.Index(fields=['start_date', 'end_date']),    # For date range queries
            models.Index(fields=['status', 'start_date']),      # For pending leaves
        ]


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
        """Validate course tracking data"""
        if self.enrollment_date and self.enrollment_date > date.today():
            raise ValidationError("Enrollment date cannot be in the future")
        
        if self.start_date and self.start_date > date.today():
            raise ValidationError("Start date cannot be in the future")
        
        if self.expected_end_date and self.expected_end_date < self.start_date:
            raise ValidationError("Expected end date cannot be before start date")
        
        if self.actual_end_date and self.actual_end_date < self.start_date:
            raise ValidationError("Actual end date cannot be before start date")
        
        if self.completion_percentage < 0 or self.completion_percentage > 100:
            raise ValidationError("Completion percentage must be between 0 and 100")

    def update_completion_percentage(self):
        """
        Update the completion percentage based on subject progress and attendance
        """
        try:
            # Get total subjects for this course
            total_subjects = Subject.objects.filter(course=self.course).count()
            if total_subjects == 0:
                self.completion_percentage = 0
                return 0

            # Get completed subjects from SubjectProgress
            completed_subjects = SubjectProgress.objects.filter(
                student=self.student,
                subject__course=self.course,
                status="Completed"
            ).count()

            # Get attendance percentage for active subjects
            attended_classes = AttendanceRecord.objects.filter(
                student=self.student,
                attendance__routine__subject__course=self.course,
                student_attend=True
            ).count()

            total_classes = AttendanceRecord.objects.filter(
                student=self.student,
                attendance__routine__subject__course=self.course
            ).count()

            # Calculate weighted completion percentage
            subject_weight = 0.7  # 70% weight to subject completion
            attendance_weight = 0.3  # 30% weight to attendance

            subject_percentage = (completed_subjects / total_subjects) * 100 if total_subjects > 0 else 0
            attendance_percentage = (attended_classes / total_classes) * 100 if total_classes > 0 else 0

            # Calculate final percentage
            completion_percentage = int(
                (subject_percentage * subject_weight) + 
                (attendance_percentage * attendance_weight)
            )

            # Ensure percentage is between 0 and 100
            completion_percentage = max(0, min(100, completion_percentage))
            
            # Update progress status based on completion
            if completion_percentage >= 100:
                self.progress_status = "Completed"
                if not self.actual_end_date:
                    self.actual_end_date = date.today()
            elif completion_percentage > 0:
                self.progress_status = "In Progress"
            else:
                self.progress_status = "Not Started"

            return completion_percentage

        except Exception as e:
            print(f"Error updating completion percentage: {str(e)}")
            return self.completion_percentage

    def calculate_completion_percentage(self):
        """Calculate completion percentage based on duration"""
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

    def save(self, *args, **kwargs):
        if not self.pk:  # New instance
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

        try:
            self.clean()
            # Update completion percentage without triggering save again
            if not hasattr(self, '_updating_completion'):
                self._updating_completion = True
                try:
                    self.completion_percentage = self.update_completion_percentage()
                finally:
                    delattr(self, '_updating_completion')
            
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
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['course']),
            models.Index(fields=['progress_status']),
            models.Index(fields=['current_period']),
            models.Index(fields=['enrollment_date']),
            models.Index(fields=['student', 'progress_status']),
            models.Index(fields=['course', 'progress_status']),
            models.Index(fields=['student', 'course', 'progress_status']),
            models.Index(fields=['completion_percentage']),
            models.Index(fields=['start_date', 'expected_end_date']),
            models.Index(fields=['current_period', 'progress_status']),
        ]


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


class OTPAttempt(models.Model):
    """Model to track OTP attempts for rate limiting"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='otp_attempts',
        null=True,
        blank=True
    )
    identifier = models.CharField(max_length=255)  # phone or email
    attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now=True)
    is_locked = models.BooleanField(default=False)
    lock_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['identifier']),
            models.Index(fields=['is_locked']),
            models.Index(fields=['lock_until']),
        ]

    def increment_attempts(self):
        """Increment attempt count and handle locking"""
        self.attempts += 1
        self.last_attempt = timezone.now()
        
        # Lock after 3 failed attempts for 15 minutes
        if self.attempts >= 3:
            self.is_locked = True
            self.lock_until = timezone.now() + timedelta(minutes=15)
        
        self.save()

    def reset_attempts(self):
        """Reset attempt count and unlock"""
        self.attempts = 0
        self.is_locked = False
        self.lock_until = None
        self.save()

    def is_locked_out(self):
        """Check if the user is currently locked out"""
        if not self.is_locked:
            return False
            
        if self.lock_until and timezone.now() > self.lock_until:
            self.reset_attempts()
            return False
            
        return True


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

    def cleanup_orphaned_data(self):
        """
        Clean up orphaned data related to this parent
        """
        # Clean up meeting records
        self.meetings.all().delete()
        
        # Clean up feedback records
        self.feedbacks.all().delete()
        self.institute_feedbacks.all().delete()
        
        # Clean up notification tokens
        self.fcm_token = None
        self.save(update_fields=['fcm_token'])

    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents"
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['is_active']),
            models.Index(fields=['phone', 'is_active']),        # For active parent lookups
        ]


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
        indexes = [
            models.Index(fields=['meeting_date']),
            models.Index(fields=['status']),
            models.Index(fields=['is_online']),
            models.Index(fields=['meeting_date', 'status']),    # For upcoming meetings
            models.Index(fields=['status', 'is_online']),       # For online meetings
        ]

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


class SubjectProgress(models.Model):
    """Model for tracking student progress in individual subjects"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subject_progress')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='student_progress')
    status = models.CharField(max_length=20, choices=PROGRESS_STATUS_CHOICES, default="Not Started")
    completion_percentage = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['student', 'subject']
        ordering = ['-last_updated']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['subject']),
            models.Index(fields=['status']),
            models.Index(fields=['student', 'subject']),
            models.Index(fields=['student', 'status']),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.subject.name}: {self.status}"
