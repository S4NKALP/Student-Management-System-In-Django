from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin import site
from app.models import (
    Student,
    NewsEvent,
    AcademicYear,
    Subject,
    Teacher,
    Staff,
    Course,
    Marksheet,
    SubjectMark,
)
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    if not request.user.is_superuser:
        return redirect("studentdashboard")

    total_student = Student.objects.count()
    total_teacher = Teacher.objects.count()
    total_staff = Staff.objects.count()
    total_course = Course.objects.count()
    total_subjects = Subject.objects.count()
    context = {
        **site.each_context(request),
        "title": "Dashboard",
        # "breadcrumbs": [{"name": "Dashboard", "url": "dashboard"}],
        "total_student": total_student,
        "total_teacher": total_teacher,
        "total_staff": total_staff,
        "total_course": total_course,
        "total_subjects": total_subjects,
    }
    return render(request, "dashboard.html", context)


@login_required
def studentdashboard(request):
    total_subject = Subject.objects.count()
    student = Student.objects.get(user=request.user)
    course_name = student.course.name
    course = student.course
    total_subjects = Subject.objects.filter(course=course).count()
    subject = Subject.objects.filter(course=course)

    context = {
        **site.each_context(request),
        "title": "Student Dashboard",
        "total_subject": total_subject,
        "course_name": course_name,
        "subject": subject,
        "total_subjects": total_subjects,
    }

    return render(request, "studentdashboard.html", context)


def marksheet(request):
    marksheet = Marksheet.objects.first()
    subject = SubjectMark.objects.filter(marksheet=marksheet)
    context = {
        **site.each_context(request),
        "title": "Marksheet",
        "marksheet": marksheet,
        "subject": subject,
    }

    return render(request, "marksheet.html", context)
