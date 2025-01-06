from django.db import models
from django.contrib.auth.models import Group
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password
import random


class BaseUser(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(
        max_length=15, validators=[RegexValidator(r"^\+?1?\d{9,15}$")]
    )
    username = models.CharField(max_length=255, unique=True, blank=True, null=True)
    password = models.CharField(max_length=255)
    active_status = models.BooleanField(default=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = f"{self.first_name.lower()}_{random.randint(1000, 9999)}"
        if self._state.adding or not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Teacher(BaseUser):
    address = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])


class Student(BaseUser):
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    academic_year = models.ForeignKey("AcademicYear", on_delete=models.CASCADE)


class Staff(BaseUser):
    position = models.CharField(
        max_length=255,
        choices=[("clerk", "Clerk"), ("assistant", "Assistant"), ("guard", "Guard")],
    )
    address = models.CharField(max_length=255)


class Course(models.Model):
    name = models.CharField(max_length=100)
    course_type = models.CharField(
        max_length=10,
        choices=[("semester", "Semester-based"), ("yearly", "Yearly-based")],
    )
    duration = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class AcademicYear(models.Model):
    batch = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"Batch {self.batch}"


class Subject(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="subjects"
    )
    semester_or_year_number = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} (Sem/Year {self.semester_or_year_number})"


class NewsEvent(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    type = models.CharField(
        max_length=5, choices=[("news", "News"), ("event", "Event")]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"
