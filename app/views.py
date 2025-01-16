from django.contrib import messages
from django.contrib.admin import site
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from app.models import (
    AcademicYear,
    Certificate,
    Course,
    Marksheet,
    NewsEvent,
    Staff,
    Student,
    Subject,
    SubjectMark,
    Teacher,
)


def view_certificate(request, pk):
    try:
        certificate = get_object_or_404(Certificate, pk=pk)
        student = certificate.student

        # Calculate GPA from marksheet if available
        gpa = None
        try:
            marksheet = Marksheet.objects.filter(student=student).latest("id")
            percentage = marksheet.obtained_marks / marksheet.total_marks * 100
            # Basic GPA calculation (customize based on your grading system)
            gpa = (percentage / 100) * 4.0
        except Marksheet.DoesNotExist:
            pass

        context = {
            **site.each_context(request),  # This adds admin context
            "certificate": certificate,
            "student": student,
            "course": student.course,
            "address": student.address,
            "dob": student.date_of_birth,
            "father": student.father_name,
            "finished_year": certificate.date,
            "principle": certificate.principle,
            "checked_by": certificate.checked_by,
            "issued_by": certificate.issued_by,
            "school_name": "XYZ Secondary School",
            "school_address": "Kohalpur, Nepal",
            "gpa": f"{gpa:.2f}" if gpa else None,
            "issue_date": certificate.date.strftime("%Y-%m-%d"),
        }
        return render(request, "Hod/view_certificate.html", context)
    except Certificate.DoesNotExist:
        return HttpResponse("Certificate not found", status=404)


# def view_certificate(request, pk):
#     try:
#         certificate = Certificate.objects.get(pk=pk)
#         students = Student.objects.get(pk=certificate.student_id)
#         context = {
#             "certificate": certificate,
#             "student": certificate.student,
#             "course": students.course,
#             "address": students.address,
#             "dob": students.date_of_birth,
#             "father": students.father_name,
#             "finished_year": certificate.date,
#             "principle": certificate.principle,
#             "checked_by": certificate.checked_by,
#             "issued_by": certificate.issued_by,
#             "school_name": "XYZ Secondary School",
#             "school_address": "Kohalpur, Nepal",
#         }
#         return render(request, "Hod/view_certificate.html", context)
#     except Certificate.DoesNotExist:
#         return HttpResponse("Certificate not found", status=404)


def get_periods(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        periods = range(1, course.duration + 1)
        return JsonResponse({"periods": list(periods)})
    except Course.DoesNotExist:
        raise Http404("Course not found.")


@login_required
def view_marksheet(request, pk):
    try:
        marksheet = Marksheet.objects.get(pk=pk)
        percentage = (
            (marksheet.obtained_marks / marksheet.total_marks) * 100
            if marksheet.total_marks > 0
            else 0
        )

        context = {
            **site.each_context(request),  # This adds admin context
            "marksheet": marksheet,
            "percentage": percentage,
            "student": marksheet.student,
            "school_name": "XYZ Secondary School",
            "theory_max": 80,
            "practical_max": 20,
            "exam_year": marksheet.student.academic_year,
        }
        return render(request, "Hod/view_marksheet.html", context)
    except Marksheet.DoesNotExist:
        return HttpResponse("Marksheet not found", status=404)


@login_required
def Add_Course(request):
    courses = Course.objects.all()

    context = {
        **site.each_context(request),  # This adds admin context
        "title": "Manage Courses",
        "courses": courses,
        "subtitle": "Course Management",
        "site_title": "School Management",
        "has_permission": True,
        "is_popup": False,
        "is_nav_sidebar_enabled": True,
        "available_apps": site.get_app_list(request),
    }

    if request.method == "POST":
        name = request.POST.get("name")
        level = request.POST.get("level")
        course_type = request.POST.get("course_type")
        duration = request.POST.get("duration")

        Course.objects.create(
            name=name, level=level, course_type=course_type, duration=duration
        )
        messages.success(request, "Course Added Successfully!")
        return redirect("add_course")

    return render(request, "Hod/add_course.html", context)


@login_required
def Edit_Course(request, id):
    course = Course.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        Course.objects.filter(id=id).update(
            name=name,
        )
        messages.success(request, "Course Updated Successfully!")
        return redirect("add_course")
    context = {
        "course": course,
    }
    return render(request, "Hod/add_course.html", context)


@login_required
def Delete_Course(request, id):
    Course.objects.filter(id=id).delete()
    messages.success(request, "Course Deleted Successfully")
    return redirect("add_course")


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
