import json
import requests
from django.contrib.admin import site
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from app.models import (
    Student,
    Teacher,
    Subject,
    Course,
    LeaveReportStudent,
    LeaveReportTeacher,
    Attendance,
    AttendanceReport,
    AcademicYear,
)
from django.contrib.auth.decorators import login_required, user_passes_test
from app.forms import SubjectForm

admin_site = site


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_home(request):
    admin_site = site
    student_count1 = Student.objects.all().count()
    teacher_count = Teacher.objects.all().count()
    subject_count = Subject.objects.all().count()
    course_count = Course.objects.all().count()
    course_all = Course.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []
    for course in course_all:
        subjects = Subject.objects.filter(course_id=course.id).count()
        students = Student.objects.filter(course_id=course.id).count()
        course_name_list.append(course.name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)

    subjects_all = Subject.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subjects_all:
        course = subject.course
        student_count = Student.objects.filter(course_id=course.id).count()
        subject_list.append(subject.name)
        student_count_list_in_subject.append(student_count)

    teacher = Teacher.objects.all()
    attendance_present_list_teacher = []
    attendance_absent_list_teacher = []
    teacher_name_list = []
    for teacher in teacher:
        subject_ids = Subject.objects.filter(teacher_id=teacher.id)
        attendance = Attendance.objects.filter(
            subject_id__in=subject_ids,
        ).count()
        leaves = LeaveReportTeacher.objects.filter(
            teacher_id=teacher.id, leave_status=1
        ).count()
        attendance_present_list_teacher.append(attendance)
        attendance_absent_list_teacher.append(leaves)
        teacher_name_list.append(teacher.first_name)

    students_all = Student.objects.all()
    attendance_present_list_student = []
    attendance_absent_list_student = []
    student_name_list = []
    for student in students_all:
        attendance = AttendanceReport.objects.filter(
            student_id=student.id, status=True
        ).count()
        absent = AttendanceReport.objects.filter(
            student_id=student.id, status=False
        ).count()
        leaves = LeaveReportStudent.objects.filter(
            student_id=student.id, leave_status=1
        ).count()
        attendance_present_list_student.append(attendance)
        attendance_absent_list_student.append(leaves + absent)
        student_name_list.append(student.admin.username)

    context = {
        **admin_site.each_context(request),
        "title": "Admin Dashboard",
        "student_count": student_count1,
        "teacher_count": teacher_count,
        "subject_count": subject_count,
        "course_count": course_count,
        "course_name_list": course_name_list,
        "subject_count_list": subject_count_list,
        "student_count_list_in_course": student_count_list_in_course,
        "student_count_list_in_subject": student_count_list_in_subject,
        "subject_list": subject_list,
        "teacher_name_list": teacher_name_list,
        "attendance_present_list_teacher": attendance_present_list_teacher,
        "attendance_absent_list_teacher": attendance_absent_list_teacher,
        "student_name_list": student_name_list,
        "attendance_present_list_student": attendance_present_list_student,
        "attendance_absent_list_student": attendance_absent_list_student,
        "opts": Student._meta,
    }
    return render(request, "hod/dashboard.html", context)


def add_course(request):
    admin_site = site
    if request.method == "POST":
        name = request.POST.get("name")
        course_type = request.POST.get("course_type")
        duration = request.POST.get("duration")

        if not name or not course_type or not duration:
            messages.error(request, "All fields are required!")
            return redirect("add_course")

        try:
            duration = int(duration)
            if duration <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Duration must be a positive number!")
            return redirect("add_course")

        if Course.objects.filter(name=name).exists():
            messages.error(request, "A course with this name already exists.")
            return redirect("add_course")

        Course.objects.create(name=name, course_type=course_type, duration=duration)
        messages.success(request, "Course added successfully!")
        return redirect("add_course")

    context = {
        **admin_site.each_context(request),
        "title": "Add Course",
        "COURSE_TYPE_CHOICES": Course.COURSE_TYPE_CHOICES,
        "opts": Course._meta,
    }
    return render(request, "hod/add_course.html", context)


def manage_course(request):
    admin_site = site
    courses = Course.objects.all()
    context = {
        **admin_site.each_context(request),
        "courses": courses,
        "title": "Manage Courses",
        "opts": Course._meta,
    }
    return render(request, "hod/manage_course.html", context)


def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        name = request.POST.get("name")
        course_type = request.POST.get("course_type")
        duration = request.POST.get("duration")

        # Validate unique name if it changed
        if name != course.name and Course.objects.filter(name=name).exists():
            messages.error(request, "A course with this name already exists.")
            return render(
                request, "edit_course.html", {"course": course, "title": "Edit Course"}
            )

        try:
            course.name = name
            course.course_type = course_type
            course.duration = duration
            course.save()

            messages.success(request, "Course updated successfully.")
            return redirect("manage_course")

        except Exception as e:
            messages.error(request, f"Error updating course: {str(e)}")

    return render(
        request, "hod/edit_course.html", {"course": course, "title": "Edit Course"}
    )


def delete_course(request, course_id):
    course = Course.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Course Deleted Successfully.")
        return redirect("manage_course")
    except:
        messages.error(request, "Failed to Delete Course.")
        return redirect("manage_course")


def add_academicyear(request):
    admin_site = site
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        academic_year = AcademicYear.objects.create(start_date=start_date)
        messages.success(request, "Academic Year added successfully.")
        return redirect("manage_academicyear")
    context = {
        **admin_site.each_context(request),
        "title": "Add Academic Year",
        "opts": AcademicYear._meta,
    }
    return render(request, "hod/add_academicyear.html", context)


def edit_academicyear(request, pk):
    academic_year = get_object_or_404(AcademicYear, pk=pk)
    admin_site = site
    if request.method == "POST":
        start_date = request.POST.get("start_date")

        if start_date:
            academic_year.start_date = start_date
            academic_year.save()
            messages.success(request, "Academic Year updated successfully.")
            return redirect("manage_academicyear")
        else:
            messages.error(request, "Please provide a valid start date.")
    context = {
        **admin_site.each_context(request),
        "title": "Edit Academic Year",
        "opts": AcademicYear._meta,
    }
    return render(
        request, "hod/edit_academicyear.html", {"academic_year": academic_year}
    )


def manage_academicyear(request):
    admin_site = site
    context = {
        **admin_site.each_context(request),
        "academic_years": AcademicYear.objects.all(),
        "title": "Manage Academic Year",
        "opts": AcademicYear._meta,
    }
    return render(request, "hod/manage_academicyear.html", context)


def delete_academicyear(request, academic_year_id):
    academic_year = AcademicYear.objects.get(id=academic_year_id)
    try:
        academic_year.delete()
        messages.success(request, "AcademicYear Deleted Successfully.")
        return redirect("manage_academicyear")
    except:
        messages.error(request, "Failed to Delete AcademicYear.")
        return redirect("manage_academicyear")


def manage_subjects(request):
    subjects = Subject.objects.all()
    courses = Course.objects.all()
    selected_course_id = request.GET.get("course")
    selected_duration = request.GET.get("duration", "")

    if selected_course_id and selected_duration:
        subjects = Subject.objects.filter(
            course_id=selected_course_id, duration=selected_duration
        )
    elif selected_course_id:
        subjects = Subject.objects.filter(course_id=selected_course_id)
    elif selected_duration:
        subjects = Subject.objects.filter(duration=selected_duration)
    else:
        subjects = Subject.objects.all()
    context = {
        **admin_site.each_context(request),
        "subjects": subjects,
        "selected_course_id": selected_course_id,
        "selected_duration": selected_duration,
        "title": "Manage Subjects",
        "courses": courses,
        "opts": Subject._meta,
    }
    return render(request, "hod/manage_subject.html", context)


def add_subject(request):
    courses = Course.objects.all()
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("manage_subjects")
    else:
        form = SubjectForm()

    context = {
        **admin_site.each_context(request),
        "title": "Add Subject",
        "courses": courses,
        "form": form,
        "opts": Subject._meta,
    }
    return render(request, "hod/add_subject.html", context)


def edit_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    courses = Course.objects.all()
    if request.method == "POST":
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect("manage_subjects")
    else:
        form = SubjectForm(instance=subject)
    context = {
        **admin_site.each_context(request),
        "title": "Add Subject",
        "courses": courses,
        "form": form,
        "opts": Subject._meta,
    }

    return render(request, "hod/edit_subject.html", context)


def delete_subject(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject Deleted Successfully.")
        return redirect("manage_subject")
    except:
        messages.error(request, "Failed to Delete Subject.")
        return redirect("manage_subject")

