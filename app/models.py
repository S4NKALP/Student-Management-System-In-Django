from django.db import models, transaction
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from datetime import date, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from .firebase import send_push_notification, FCMDevice

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
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

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
    duration = models.IntegerField(default=1, null=True, blank=True)
    duration_type = models.CharField(max_length=255, choices=DURATION_TYPES, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"

class Subject(models.Model):
    """Model representing a subject within a course"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester_or_year = models.PositiveIntegerField()
    syllabus_pdf = models.FileField(
        upload_to="subject_pdfs/",
        null=True,
        blank=True,
        help_text="Upload syllabus or study material PDF",
    )

    def __str__(self):
        return f"{self.name} ({self.course.name} - {'Semester' if self.course.duration_type == 'Semester' else 'Year'} {self.semester_or_year})"

    def clean(self):
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
        return self.syllabus_pdf.url if self.syllabus_pdf else None

    def get_all_files(self):
        """Get all files associated with this subject including syllabus and additional files"""
        files = []
        if self.syllabus_pdf:
            files.append({
                "id": "syllabus",
                "title": f"{self.name} Syllabus",
                "description": f"Syllabus PDF for {self.name}",
                "file_url": self.syllabus_pdf.url,
                "file_type": "syllabus",
                "uploaded_by": None,
                "uploaded_at": None
            })
        
        subject_files = self.subjectfile_set.all().order_by('-uploaded_at')
        for file in subject_files:
            files.append({
                "id": file.id,
                "title": file.title,
                "description": file.description,
                "file_url": file.file.url,
                "file_type": "notes",
                "uploaded_by": file.uploaded_by.name if file.uploaded_by else None,
                "uploaded_at": file.uploaded_at
            })
        
        return files

    class Meta:
        unique_together = ["name", "course", "semester_or_year"]
        ordering = ["course", "semester_or_year", "name"]

class SubjectFile(models.Model):
    """Model to store additional files for subjects (notes, study materials, etc.)"""
    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to="subject_files/")
    uploaded_by = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"
    
    class Meta:
        ordering = ['-uploaded_at']

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
    status = models.CharField(max_length=255, choices=STUDENT_STATUS_CHOICES, null=True, blank=True)
    gender = models.CharField(max_length=255, choices=GENDER_CHOICES, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True, unique=True)
    temporary_address = models.CharField(max_length=500, null=True, blank=True)
    permanent_address = models.CharField(max_length=500, null=True, blank=True)
    marital_status = models.CharField(max_length=255, choices=MARITAL_STATUS_CHOICES, null=True, blank=True)
    parent_name = models.CharField(max_length=255, null=True, blank=True)
    parent_phone = models.CharField(max_length=255, null=True, blank=True)
    citizenship_no = models.CharField(max_length=255, null=True, blank=True)
    batches = models.ManyToManyField('Batch', related_name="students", blank=True)
    image = models.ImageField(upload_to="student_image", null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    current_semester = models.PositiveIntegerField(default=1, help_text="Current semester for semester-based courses")
    joining_date = models.DateField(null=True, blank=True)
    password = models.CharField(max_length=128, editable=False, null=True)
    fcm_token = models.CharField(max_length=500, null=True, blank=True)

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
            perms.update(group.permissions.values_list("content_type__app_label", "codename"))

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
            course=self.course,
            semester_or_year=self.current_semester
        )

    def advance_semester(self):
        """Advance to next semester if possible"""
        if not self.course:
            return False

        if self.course.duration_type == "Semester":
            total_semesters = self.course.duration * 2
            if self.current_semester < total_semesters:
                self.current_semester += 1
                self.save()
                return True
        return False

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
    is_staff = models.BooleanField(default=True)
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
    gender = models.CharField(max_length=255, choices=GENDER_CHOICES, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    temporary_address = models.CharField(max_length=255, null=True, blank=True)
    permanent_address = models.CharField(max_length=255, null=True, blank=True)
    marital_status = models.CharField(max_length=255, choices=MARITAL_STATUS_CHOICES, null=True, blank=True)
    parent_name = models.CharField(max_length=255, null=True, blank=True)
    parent_phone = models.CharField(max_length=255, null=True, blank=True)
    citizenship_no = models.CharField(max_length=255, blank=True, null=True)
    passport = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to="staff_image", null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    password = models.CharField(max_length=128, editable=False, null=True)
    fcm_token = models.CharField(max_length=500, null=True, blank=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save(update_fields=["password"])

    @property
    def is_staff(self):
        return True

    @property
    def is_authenticated(self):
        return True

    def has_perm(self, perm, obj=None):
        if not self.is_active:
            return False

        perms = set()
        for group in self.groups.all():
            perms.update(group.permissions.values_list("content_type__app_label", "codename"))

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
    semester_or_year = models.PositiveIntegerField()
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
            "semester_or_year",
        ]

# Attendance Models
class Attendance(models.Model):
    """Model representing attendance records"""
    id = models.BigAutoField(primary_key=True)
    date = models.DateField()
    routine = models.ForeignKey(Routine, related_name="attendances", on_delete=models.CASCADE, null=True, blank=True)
    teacher = models.ForeignKey(Staff, related_name="attendances", on_delete=models.CASCADE, null=True, blank=True)
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
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, null=True, blank=True, related_name="records")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name="attendance_records")
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

    def save(self, *args, **kwargs):
        send_push_notification(
            self.title, self.message, FCMDevice.objects.values_list("token", flat=True)
        )
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Notice"
        verbose_name_plural = "Notices"

# Leave Models
class Staff_leave(models.Model):
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

class Student_Leave(models.Model):
    """Model representing student leave requests"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
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
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="feedbacks")
    teacher = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="feedbacks")
    rating = models.DecimalField(max_digits=2, decimal_places=1, choices=[(i / 2, i / 2) for i in range(2, 11)])
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
    """Model representing student feedback for the institute"""
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="feedbacks")
    user = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="institute_feedbacks")
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES, default="General")
    rating = models.DecimalField(max_digits=2, decimal_places=1, choices=[(i / 2, i / 2) for i in range(2, 11)])
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
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name="staff_feedbacks")
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="institute_feedbacks")
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES, default="General")
    rating = models.DecimalField(max_digits=2, decimal_places=1, choices=[(i / 2, i / 2) for i in range(2, 11)])
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

# Course Tracking Model
class CourseTracking(models.Model):
    """Model for tracking student progress in courses"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="course_trackings")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="student_trackings")
    enrollment_date = models.DateField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    expected_end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    progress_status = models.CharField(max_length=20, choices=PROGRESS_STATUS_CHOICES, default="Not Started")
    completion_percentage = models.IntegerField(default=0, help_text="Percentage of course completion (0-100)")
    current_semester = models.PositiveIntegerField(default=1)
    semester_start_date = models.DateField(null=True, blank=True)
    semester_end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"

    def clean(self):
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
            total_semesters = self.course.duration * 2
            completed_semesters = self.current_semester - 1
            semester_progress = (completed_semesters / total_semesters) * 100

            if self.semester_end_date and today > self.semester_end_date:
                semester_progress = (self.current_semester / total_semesters) * 100

            return min(100, int(semester_progress))
        else:  # Yearly based
            max_days = 365
            if elapsed_days >= max_days:
                return 100

        percentage = min(100, int((elapsed_days / total_duration) * 100))
        return percentage

    def get_completion_percentage(self):
        return self.completion_percentage

    def update_completion_percentage(self):
        new_percentage = self.calculate_completion_percentage()
        if new_percentage != self.completion_percentage:
            self.completion_percentage = new_percentage
            self.save(update_fields=['completion_percentage'])
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

            self.semester_start_date = self.start_date
            self.semester_end_date = self.start_date + timedelta(days=180)  # 6 months

        self.clean()
        self.completion_percentage = self.calculate_completion_percentage()

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
        if not self.course:
            return False

        if self.course.duration_type == "Semester":
            total_semesters = self.course.duration * 2
            if self.current_semester < total_semesters:
                self.current_semester += 1
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
        if not self.semester_end_date:
            return 0
        return max(0, (self.semester_end_date - date.today()).days)

    @property
    def total_remaining_days(self):
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
            models.Index(fields=['identifier']),
            models.Index(fields=['expires_at']),
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
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

    def is_expired(self):
        return timezone.now() > self.expires_at
