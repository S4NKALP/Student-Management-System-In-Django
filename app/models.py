from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password
import random
from decimal import Decimal


# Abstract BaseUser Model
class BaseUser(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(
        max_length=10, validators=[RegexValidator(r"^\+?1?\d{9,15}$")]
    )
    username = models.CharField(max_length=255, unique=True, blank=True, null=True)
    password = models.CharField(max_length=255)
    active_status = models.BooleanField(default=True)
    group = models.ManyToManyField(Group, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Generate a username if not provided
        if not self.username:
            self.username = f"{self.first_name.lower()}_{random.randint(1000, 9999)}"

        # Hash the password if new or not already hashed
        if self._state.adding or not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)

        # Create or update the linked User object
        if not self.user:
            self.user = User.objects.create(
                username=self.username,
                email=self.email,
                first_name=self.first_name,
                last_name=self.last_name,
                is_staff=True,
                is_active=self.active_status,
                password=self.password,
            )
        else:
            self.user.username = self.username
            self.user.email = self.email
            self.user.first_name = self.first_name
            self.user.last_name = self.last_name
            self.user.is_active = self.active_status
            self.user.is_staff = True
            self.user.password = self.password

        # Save the BaseUser instance
        super().save(*args, **kwargs)

        # Update the user's groups
        self.user.groups.set(self.group.all())

        # Save the user object
        self.user.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Teacher model
class Teacher(BaseUser):
    address = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])


# Student model
class Student(BaseUser):
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    academic_year = models.ForeignKey("AcademicYear", on_delete=models.CASCADE)


# Staff model
class Staff(BaseUser):
    position = models.CharField(
        max_length=255,
        choices=[("clerk", "Clerk"), ("assistant", "Assistant"), ("guard", "Guard")],
    )
    address = models.CharField(max_length=255)


# Course model
class Course(models.Model):
    name = models.CharField(max_length=100)
    course_type = models.CharField(
        max_length=10,
        choices=[("semester", "Semester-based"), ("yearly", "Yearly-based")],
    )
    duration = models.PositiveIntegerField()

    def __str__(self):
        return self.name


# AcademicYear model
class AcademicYear(models.Model):
    batch = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.batch


# Subject model
class Subject(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="subjects"
    )
    semester_or_year_number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} (Sem/Year {self.semester_or_year_number})"


# NewsEvent model
class NewsEvent(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    type = models.CharField(
        max_length=5, choices=[("news", "News"), ("event", "Event")]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"


# Attendance model
class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    subject = models.ForeignKey("Subject", on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(
        max_length=10, choices=[("present", "Present"), ("absent", "Absent")]
    )


# Result model
class Result(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    subject = models.ForeignKey("Subject", on_delete=models.CASCADE)
    practical_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    exam_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    total_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"), editable=False
    )

    def clean(self):
        self.total_marks = self.get_total()
        super().clean()

    def get_total(self):
        return Decimal(str(self.practical_marks or 0)) + Decimal(
            str(self.exam_marks or 0)
        )

    def save(self, *args, **kwargs):
        self.total_marks = self.get_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.subject} - Total: {self.total_marks}"
