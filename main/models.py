from django.db import models
import random
from django.core.validators import RegexValidator
from django.contrib.auth.models import Group
# Create your models here.


class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$", "Enter a valid phone number.")],
    )
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    active_status = models.BooleanField(default=True)
    username = models.CharField(max_length=255, unique=True, blank=True, null=True)
    password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.username:
            random_number = random.randint(1000, 9999)
            self.username = f"{self.first_name.lower()}_{random_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    active_status = models.BooleanField(default=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])
    phone = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(r"^\d{10}$", "Enter a valid 10-digit phone number.")
        ],
    )
    email = models.EmailField(max_length=255, unique=True)
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    academic_year = models.ForeignKey("AcademicYear", on_delete=models.CASCADE)
    username = models.CharField(max_length=255, unique=True, blank=True, null=True)
    password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.username:
            random_number = random.randint(1000, 9999)
            self.username = f"{self.first_name.lower()}_{random_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Staff(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    position = models.CharField(
        max_length=255,
        choices=[("clerk", "Clerk"), ("assistant", "Assistant"), ("guard", "Guard")],
    )
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$", "Enter a valid phone number.")],
    )
    active_status = models.BooleanField(default=True)
    username = models.CharField(max_length=255, unique=True, blank=True, null=True)
    password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.username:
            random_number = random.randint(1000, 9999)
            self.username = f"{self.first_name.lower()}_{random_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    COURSE_TYPE_CHOICES = [
        ("semester", "Semester-based"),
        ("yearly", "Yearly-based"),
    ]
    name = models.CharField(max_length=100)
    academic_year = models.ForeignKey("AcademicYear", on_delete=models.CASCADE)
    course_type = models.CharField(max_length=10, choices=COURSE_TYPE_CHOICES)
    duration = models.PositiveIntegerField(help_text="Number of semesters or years")

    def __str__(self):
        return self.name


class AcademicYear(models.Model):
    id = models.AutoField(primary_key=True)
    batch = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"Batch {self.batch}"


class Subject(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="subjects"
    )
    semester_or_year_number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} (Sem/Year {self.semester_or_year_number})"


class NewsEvent(models.Model):
    TYPE_CHOICES = [
        ("news", "News"),
        ("event", "Event"),
    ]
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    summary = models.TextField()
    type = models.CharField(max_length=5, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"


USER_CHOICES = [
    ("staff", "Staff"),
    ("teacher", "Teacher"),
    ("student", "Student"),
]
