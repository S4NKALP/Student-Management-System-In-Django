import random
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, Group, User
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models


# Abstract BaseUser Model
class BaseUser(models.Model):
    is_active = models.BooleanField(default=True)
    group = models.ManyToManyField(Group, blank=True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(
        max_length=10, validators=[RegexValidator(r"^\+?1?\d{9,15}$")]
    )
    username = models.CharField(max_length=255, unique=True, blank=True, null=True)
    password = models.CharField(max_length=255)
    # group = models.ManyToManyField(Group, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = f"{self.first_name.lower()}_{random.randint(1000, 9999)}"

        if self._state.adding or not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)

        if not self.user:
            self.user = User.objects.create(
                username=self.username,
                email=self.email,
                first_name=self.first_name,
                last_name=self.last_name,
                is_staff=True,
                is_active=self.is_active,
                password=self.password,
            )
        else:
            self.user.username = self.username
            self.user.email = self.email
            self.user.first_name = self.first_name
            self.user.last_name = self.last_name
            self.user.is_active = self.is_active
            self.user.is_staff = True
            self.user.password = self.password

        super().save(*args, **kwargs)
        if hasattr(self, "group") and self.group.exists():
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


# Course model
class Course(models.Model):
    name = models.CharField(max_length=100)
    level_choice = (
        ("basic", "Basic"),
        ("primary", "Primary"),
        ("secondary", "Secondary"),
        ("vocational training", "Vocational Training"),
        ("higher secondary", "Higher Secondary"),
        ("graduation", "Graduation"),
        ("post graduation", "Post Graduation"),
    )
    level = models.CharField(choices=level_choice, max_length=45)
    course_type = models.CharField(
        max_length=10,
        choices=[("semester", "Semester-based"), ("yearly", "Yearly-based")],
    )
    duration = models.PositiveIntegerField()

    @property
    def duration_display(self):
        if self.course_type == "semester":
            return (
                f"{self.duration} {'Semester' if self.duration == 1 else 'Semesters'}"
            )
        else:
            return f"{self.duration} {'Year' if self.duration == 1 else 'Years'}"

    def __str__(self):
        return f"{self.name} "

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"


# AcademicYear model
class AcademicYear(models.Model):
    year = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.year

    class Meta:
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"


# Student model
class Student(BaseUser):
    date_of_birth = models.DateField(blank=False)
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])
    address = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    father_name = models.CharField(max_length=100)
    father_phone_no = models.CharField(
        max_length=10, validators=[RegexValidator(r"^\+?1?\d{9,15}$")]
    )
    father_email = models.EmailField(blank=True, null=True)
    occupation_choice = (
        ("agriculture", "Agriculture"),
        ("banker", "Banker"),
        ("business", "Business"),
        ("doctor", "Doctor"),
        ("farmer", "Farmer"),
        ("fisherman", "Fisherman"),
        ("public service", "Public Service"),
        ("private service", "Private Service"),
        ("shopkeeper", "Shopkeeper"),
        ("driver", "Driver"),
        ("housewife", "HouseWife"),
        ("worker", "Worker"),
        ("N/A", "N/A"),
    )
    father_occupation = models.CharField(
        choices=occupation_choice, max_length=45, default="N/A"
    )
    mother_name = models.CharField(max_length=100)
    mother_phone_no = models.CharField(
        max_length=10,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$")],
        blank=True,
        null=True,
    )
    mother_email = models.EmailField(blank=True, null=True)
    mother_occupation = models.CharField(
        choices=occupation_choice, max_length=45, default="N/A"
    )
    guardian_name = models.CharField(max_length=100)
    guardian_phone_no = models.CharField(
        max_length=10, validators=[RegexValidator(r"^\+?1?\d{9,15}$")]
    )
    guardian_email = models.EmailField(blank=True, null=True)
    relationship_choice = (
        ("father", "Father"),
        ("mother", "Mother"),
        ("brother", "Brother"),
        ("sister", "Sister"),
        ("uncle", "Uncle"),
        ("aunt", "Aunt"),
        ("grandfather", "Grandfather"),
    )
    relationship_with_student = models.CharField(
        choices=relationship_choice, max_length=45
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if hasattr(self, "group") and self.group.exists():
            if hasattr(self, "user"):
                self.user.groups.set(self.group.all())
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"


# Staff model
class Staff(BaseUser):
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])
    position = models.CharField(
        max_length=255,
        choices=[
            ("lab Assistant", "Lab Assistant"),
            ("librarian", "Librarian"),
            ("accountant", "Accountant"),
            ("guard", "Guard"),
            ("driver", "Driver"),
            ("helper", "Helper"),
            ("cleaner", "Cleaner"),
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


# Subject model
class Subject(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="subjects"
    )
    semester_or_year_number = models.PositiveIntegerField()
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="subjects",
        null=True,
        blank=True,
    )

    @property
    def period_display(self):
        period_type = "Semester" if self.course.course_type == "semester" else "Year"
        return f"{period_type} {self.semester_or_year_number}"

    def __str__(self):
        return f"{self.name} ({self.period_display})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.semester_or_year_number > self.course.duration:
            period_type = (
                "semester" if self.course.course_type == "semester" else "year"
            )
            raise ValidationError(
                f"The {period_type} number cannot be greater than the course duration "
                f"({self.course.duration})"
            )

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ["course", "semester_or_year_number", "name"]


# NewsEvent model
class NewsEvent(models.Model):
    class NewsEventType(models.TextChoices):
        NEWS = "news", "News"
        EVENT = "event", "Event"

    title = models.CharField(max_length=255)
    summary = models.TextField()
    type = models.CharField(max_length=5, choices=NewsEventType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.type})"

    class Meta:
        verbose_name = "News/Event"
        verbose_name_plural = "News/Events"


# Attendance model
class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    session_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
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
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    practical_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )
    exam_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )
    total_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0"), editable=False
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
    publication = models.CharField(max_length=255)
    publication_year = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    available = models.CharField(max_length=1, choices=[("Y", "Yes"), ("N", "NO")])
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.book_name

    class Meta:
        verbose_name = "Library"
        verbose_name_plural = "Library"


class Marksheet(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="marksheets"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="marksheets"
    )
    period_number = models.PositiveIntegerField(
        help_text="Select the semester/year number within the course duration."
    )
    total_marks = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        default=Decimal("0.00"),
        blank=True,
        null=True,
    )
    obtained_marks = models.PositiveIntegerField(
        validators=[MinValueValidator(0)], default=Decimal("0.00")
    )
    grade = models.CharField(
        max_length=2,
        choices=[
            ("A+", "A+"),
            ("A", "A"),
            ("B+", "B+"),
            ("B", "B"),
            ("C+", "C+"),
            ("C", "C"),
            ("D", "D"),
            ("E", "E"),
        ],
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Marksheet"
        verbose_name_plural = "Marksheets"
        unique_together = ("student", "course", "period_number")

    def calculate_totals(self):
        subject_marks = self.subject_marks.all()
        total_marks = sum(
            subject.total_practical_marks + subject.total_theory_marks
            for subject in subject_marks
        ) or Decimal("0.00")
        obtained_marks = sum(
            subject.obtained_practical_marks + subject.obtained_theory_marks
            for subject in subject_marks
        ) or Decimal("0.00")
        return total_marks, obtained_marks

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)

        if self.period_number > self.course.duration:
            raise ValueError(
                f"The period number cannot exceed the course duration ({self.course.duration})."
            )

        self.total_marks, self.obtained_marks = self.calculate_totals()

        if self.total_marks > 0:
            percentage = (self.obtained_marks / self.total_marks) * 100
            if percentage >= 90:
                self.grade = "A+"
            elif percentage >= 80:
                self.grade = "A"
            elif percentage >= 70:
                self.grade = "B+"
            elif percentage >= 60:
                self.grade = "B"
            elif percentage >= 50:
                self.grade = "C+"
            elif percentage >= 40:
                self.grade = "C"
            elif percentage >= 30:
                self.grade = "D"
            else:
                self.grade = "E"

        super().save(*args, **kwargs)

    def __str__(self):
        period_type = "Semester" if self.course.course_type == "semester" else "Year"
        return f"{self.student} - {period_type} {self.period_number}"


class SubjectMark(models.Model):
    marksheet = models.ForeignKey(
        Marksheet, on_delete=models.CASCADE, related_name="subject_marks"
    )
    subject = models.ForeignKey(
        "Subject", on_delete=models.CASCADE, related_name="subject_marks"
    )
    obtained_practical_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    total_practical_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("20.00")
    )
    obtained_theory_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    total_theory_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("80.00")
    )
    total_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )

    def get_total(self):
        return Decimal(str(self.obtained_practical_marks or 0)) + Decimal(
            str(self.obtained_theory_marks or 0)
        )

    def save(self, *args, **kwargs):
        self.total_marks = self.get_total()
        super().save(*args, **kwargs)
        self.marksheet.save()

    class Meta:
        unique_together = ("marksheet", "subject")

    def __str__(self):
        return f"{self.subject.name} - {self.marksheet.student.first_name}"


class Certificate(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="certificate"
    )
    finished_year = models.CharField(max_length=5)
    issued_by = models.CharField(max_length=255)
    checked_by = models.CharField(max_length=255)
    principle = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return f"Certificate for {self.student.first_name} {self.student.last_name}"


class ClassRoutine(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()


class Complaint(models.Model):
    id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.subject


class Notes(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    notes = models.FileField(upload_to="media/notes")

    def __str__(self):
        return self.subject.name


class StudentLeave(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    message = models.TextField()
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student_id.first_name + self.student_id.last_name


class TeacherLeave(models.Model):
    teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateField()
    message = models.TextField()
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.teacher_id.first_name + self.teacher_id.last_name


class FeedbackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.feedback


class FeedbackTeacher(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.feedback


class StudyMaterial(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    resource_type = models.CharField(
        max_length=7, choices=[("Video", "Video"), ("Article", "Article")]
    )
    url = models.URLField()

    def __str__(self):
        return self.subject.name


class Syllabus(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    syllabus_file = models.FileField(upload_to="media/syllabus")

    def __str__(self):
        return self.course.name
