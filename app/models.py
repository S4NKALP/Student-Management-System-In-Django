from django.db import models
from django.core.validators import RegexValidator, ValidationError
from django.contrib.auth.models import User
# Create your models here.


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255)
    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="students"
    )
    academic_year = models.ForeignKey(
        "AcademicYear", on_delete=models.CASCADE, related_name="students"
    )
    password = models.CharField(max_length=255)
    fcm_token = models.TextField(default="")
    phone = models.CharField(
        max_length=10, validators=[RegexValidator(r"^\+?1?\d{9,15}$")]
    )
    email = models.EmailField(max_length=255, unique=True)
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])
    address = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    parents_number = models.CharField(
        max_length=10, validators=[RegexValidator(r"^\+?1?\d{9,15}$")]
    )
    occupation_choice = (
        ("business", "Business"),
        ("doctor", "Doctor"),
        ("farmer", "Farmer"),
        ("teacher", "teacher"),
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
    mother_occupation = models.CharField(
        choices=occupation_choice, max_length=45, default="N/A"
    )
    guardian_name = models.CharField(max_length=255)
    guardian_number = models.CharField(
        max_length=10, validators=[RegexValidator(r"^\+?1?\d{9,15}$")]
    )
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(
        max_length=10, validators=[RegexValidator(r"^\+?1?\d{9,15}$")]
    )
    email = models.EmailField(max_length=255, unique=True)
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])
    address = models.CharField(max_length=255)
    fcm_token = models.TextField(default="")
    password = models.CharField(max_length=255)
    qualification_choice = (
        ("SLC", "SLC"),
        ("Intermediate", "Intermediate"),
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
    specialization_on = models.CharField(max_length=255)
    marital_status_choice = (
        ("married", "Married"),
        ("widowed", "Widowed"),
        ("separated", "Separated"),
        ("divorced", "Divorced"),
        ("single", "Single"),
    )
    marital_status = models.CharField(choices=marital_status_choice, max_length=10)
    date_of_joining = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name + "" + self.middle_name + "" + self.last_name


class AcademicYear(models.Model):
    id = models.AutoField(primary_key=True)
    start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.start_date)


class Course(models.Model):
    SEMESTER = "semester"
    YEAR = "year"

    COURSE_TYPE_CHOICES = [
        (SEMESTER, "Semester-based"),
        (YEAR, "Year-based"),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    course_type = models.CharField(max_length=10, choices=COURSE_TYPE_CHOICES)
    duration = models.PositiveIntegerField(help_text="Duration in months")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_course_type_display()})"


class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="subjects"
    )
    duration = models.PositiveIntegerField(
        help_text="For semester-based courses, specify the semester number. For year-based courses, specify the year."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.course.name}, Duration: {self.duration})"

    def clean(self):
        if (
            self.course.course_type == Course.SEMESTER
            and self.duration > self.course.duration
        ):
            raise ValidationError(
                f"Duration (semester) must not exceed the course's total semesters ({self.course.duration})."
            )
        if (
            self.course.course_type == Course.YEAR
            and self.duration > self.course.duration
        ):
            raise ValidationError(
                f"Duration (year) must not exceed the course's total years ({self.course.duration})."
            )


class Attendance(models.Model):  # Subject Attendance
    id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    attendance_date = models.DateField()
    academic_year_id = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AttendanceReport(models.Model):  # Individual Student Attendance
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class LeaveReportStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    leave_date = models.DateField()
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportTeacher(models.Model):
    id = models.AutoField(primary_key=True)
    teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    leave_date = models.DateField()
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackTeacher(models.Model):
    id = models.AutoField(primary_key=True)
    teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
