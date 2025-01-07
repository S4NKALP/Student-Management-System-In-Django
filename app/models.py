from django.db import models
from django.contrib.auth.models import User, Group
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password
import random
from decimal import Decimal
from datetime import time, timedelta, datetime


# Abstract BaseUser Model
class BaseUser(models.Model):
    active_status = models.BooleanField(default=True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(
        max_length=10, validators=[RegexValidator(r"^\+?1?\d{9,15}$")]
    )
    username = models.CharField(max_length=255, unique=True, blank=True, null=True)
    password = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
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

        # Sync with Django User model
        if not self.user:
            self.user = User.objects.create(
                username=self.username,
                email=self.email,
                first_name=self.first_name,
                last_name=self.last_name,
                address=self.address,
                is_staff=True,
                is_active=self.active_status,
                password=self.password,
            )
        else:
            self.user.username = self.username
            self.user.email = self.email
            self.user.first_name = self.first_name
            self.user.last_name = self.last_name
            self.user.address = self.address
            self.user.is_active = self.active_status
            self.user.is_staff = True
            self.user.password = self.password

        super().save(*args, **kwargs)
        self.user.groups.set(self.group.all())
        self.user.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Teacher model
class Teacher(BaseUser):
    address = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])
    qualification_choice = (
        ("BA", "BA"),
        ("BBS", "BBS"),
        ("BE", "BE"),
        ("BEd", "BEd"),
        ("BSc", "BSc"),
        ("MA", "MA"),
        ("MSc", "MSc"),
        ("MBS", "MBS"),
        ("ME", "ME"),
        ("PhD", "PhD"),
        ("Others", "Others"),
    )
    qualification = models.CharField(choices=qualification_choice, max_length=45)
    specialization = models.CharField(max_length=255)
    marital_status_choice = (
        ("married", "Married"),
        ("widowed", "Widowed"),
        ("separated", "Separated"),
        ("divorced", "Divorced"),
        ("single", "Single"),
    )
    marital_status = models.CharField(choices=marital_status_choice, max_length=10)
    date_of_joining = models.DateField()

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"


# Student model
class Student(BaseUser):
    date_of_birth = models.DateField(blank=False)
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    academic_year = models.ForeignKey("AcademicYear", on_delete=models.CASCADE)
    father_name = models.CharField(max_length=100)
    father_phone_no = models.CharField(
        max_length=10, validators=[RegexValidator(r"^\+?1?\d{9,15}$")]
    )
    father_email = models.EmailField(blank=True, null=True)
    father_occupation_choice = (
        ("Agriculture", "Agriculture"),
        ("Banker", "Banker"),
        ("Business", "Business"),
        ("Doctor", "Doctor"),
        ("Farmer", "Farmer"),
        ("Fisherman", "Fisherman"),
        ("Public Service", "Public Service"),
        ("Private Service", "Private Service"),
        ("Shopkeeper", "Shopkeeper"),
        ("Driver", "Driver"),
        ("Worker", "Worker"),
        ("N/A", "N/A"),
    )
    father_occupation = models.CharField(
        choices=father_occupation_choice, max_length=45, default="N/A"
    )
    mother_name = models.CharField(max_length=100)
    mother_phone_no = models.CharField(
        max_length=10,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$")],
        blank=True,
        null=True,
    )
    mother_email = models.EmailField(blank=True, null=True)
    mother_occupation_choice = (
        ("Agriculture", "Agriculture"),
        ("Banker", "Banker"),
        ("Business", "Business"),
        ("Doctor", "Doctor"),
        ("Farmer", "Farmer"),
        ("Fisherman", "Fisherman"),
        ("Public Service", "Public Service"),
        ("Private Service", "Private Service"),
        ("Shopkeeper", "Shopkeeper"),
        ("Driver", "Driver"),
        ("HouseWife", "HouseWife"),
        ("Worker", "Worker"),
        ("N/A", "N/A"),
    )
    mother_occupation = models.CharField(
        choices=mother_occupation_choice, max_length=45, default="N/A"
    )
    guardian_name = models.CharField(max_length=100)
    guardian_phone_no = models.CharField(
        max_length=10, validators=[RegexValidator(r"^\+?1?\d{9,15}$")]
    )
    guardian_email = models.EmailField(blank=True, null=True)
    relationship_choice = (
        ("Father", "Father"),
        ("Mother", "Mother"),
        ("Brother", "Brother"),
        ("Sister", "Sister"),
        ("Uncle", "Uncle"),
        ("Aunt", "Aunt"),
        ("Grandfather", "Grandfather"),
    )
    relationship_with_student = models.CharField(
        choices=relationship_choice, max_length=45
    )

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"


# Staff model
class Staff(BaseUser):
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])
    position = models.CharField(
        max_length=255,
        choices=[
            ("Lab Assistant", "Lab Assistant"),
            ("Librarian", "Librarian"),
            ("Accountant", "Accountant"),
            ("Guard", "Guard"),
            ("Driver", "Driver"),
            ("Helper", "Helper"),
            ("Cleaner", "Cleaner"),
        ],
    )
    address = models.CharField(max_length=255)
    marital_status_choice = (
        ("married", "Married"),
        ("widowed", "Widowed"),
        ("separated", "Separated"),
        ("divorced", "Divorced"),
        ("single", "Single"),
    )
    marital_status = models.CharField(choices=marital_status_choice, max_length=10)
    date_of_joining = models.DateField()

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staff"


# Course model
class Course(models.Model):
    name = models.CharField(max_length=100)
    level_choice = (
        ("Basic", "Basic"),
        ("Primary", "Primary"),
        ("Secondary", "Secondary"),
        ("Vocational Traning", "Vocational Traning"),
        ("Higher Secondary", "Higher Secondary"),
        ("Graduation", "Graduation"),
        ("Post Graduation", "Post Graduation"),
    )
    level = models.CharField(choices=level_choice, max_length=45)
    course_type = models.CharField(
        max_length=10,
        choices=[("semester", "Semester-based"), ("yearly", "Yearly-based")],
    )
    duration = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"


# AcademicYear model
class AcademicYear(models.Model):
    year = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.batch

    class Meta:
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"


# Subject model
class Subject(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="subjects"
    )
    semester_or_year_number = models.PositiveIntegerField()
    teacher = models.ForeignKey(
        "Teacher",
        on_delete=models.CASCADE,
        related_name="subjects",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name} (Sem/Year {self.semester_or_year_number})"

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"


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

    class Meta:
        verbose_name = "News/Event"
        verbose_name_plural = "News/Events"


# Attendance model
class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    subject = models.ForeignKey("Subject", on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(
        max_length=10, choices=[("present", "Present"), ("absent", "Absent")]
    )

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance Records"


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

    def get_total(self):
        return Decimal(str(self.practical_marks or 0)) + Decimal(
            str(self.exam_marks or 0)
        )

    def save(self, *args, **kwargs):
        self.total_marks = self.get_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.subject} - Total: {self.total_marks}"

    class Meta:
        verbose_name = "Result"
        verbose_name_plural = "Results"


class Library(models.Model):
    category = models.CharField(max_length=255)
    book_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publication_year = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    available = models.CharField(max_length=1, choices=[("Y", "Yes"), ("N", "NO")])
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.book_name

    class Meta:
        verbose_name = "Library"
        verbose_name_plural = "Library"
