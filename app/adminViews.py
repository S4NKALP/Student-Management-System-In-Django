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
    FeedbackStudent,
    FeedbackTeacher,
)
from django.contrib.auth.decorators import login_required, user_passes_test
from app.forms import SubjectForm

admin_site = site


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_home(request):
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

    # subjects_all = Subject.objects.all()
    # subject_list = []
    # student_count_list_in_subject = []
    # for subject in subjects_all:
    #     course = subject.course
    #     student_count = Student.objects.filter(course_id=course.id).count()
    #     subject_list.append(subject.name)
    #     student_count_list_in_subject.append(student_count)

    # teacher = Teacher.objects.all()
    # attendance_present_list_teacher = []
    # attendance_absent_list_teacher = []
    # teacher_name_list = []
    # for teacher in teacher:
    #     subject_ids = Subject.objects.filter(teacher=teacher).values_list(
    #         "id", flat=True
    #     )
    #     attendance = Attendance.objects.filter(
    #         subject_id__in=subject_ids,
    #     ).count()
    #     leaves = LeaveReportTeacher.objects.filter(
    #         teacher_id=teacher.id, leave_status=1
    #     ).count()
    #     attendance_present_list_teacher.append(attendance)
    #     attendance_absent_list_teacher.append(leaves)
    #     teacher_name_list.append(teacher.first_name)

    # students_all = Student.objects.all()
    # attendance_present_list_student = []
    # attendance_absent_list_student = []
    # student_name_list = []
    # for student in students_all:
    #     attendance = AttendanceReport.objects.filter(
    #         student_id=student.id, status=True
    #     ).count()
    #     absent = AttendanceReport.objects.filter(
    #         student_id=student.id, status=False
    #     ).count()
    #     leaves = LeaveReportStudent.objects.filter(
    #         student_id=student.id, leave_status=1
    #     ).count()
    #     attendance_present_list_student.append(attendance)
    #     attendance_absent_list_student.append(leaves + absent)
    # student_name_list.append(student.username)

    context = {
        **admin_site.each_context(request),
        "title": "Admin Dashboard",
        "student_count": student_count1,
        "teacher_count": teacher_count,
        "subject_count": subject_count,
        "course_count": course_count,
        # "course_name_list": course_name_list,
        "subject_count_list": subject_count_list,
        # "student_count_list_in_course": student_count_list_in_course,
        # "student_count_list_in_subject": student_count_list_in_subject,
        # "subject_list": subject_list,
        # "teacher_name_list": teacher_name_list,
        # "attendance_present_list_teacher": attendance_present_list_teacher,
        # "attendance_absent_list_teacher": attendance_absent_list_teacher,
        # "student_name_list": student_name_list,
        # "attendance_present_list_student": attendance_present_list_student,
        # "attendance_absent_list_student": attendance_absent_list_student,
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
    context = {
        **admin_site.each_context(request),
        "title": "Edit Course",
        "course": course,
    }
    return render(request, "hod/edit_course.html", context)


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
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        academic_year = AcademicYear.objects.create(start_date=start_date)
        messages.success(request, "Academic Year added successfully.")
        return redirect("manage_academicyear")
    context = {
        **admin_site.each_context(request),
        "title": "Add Academic Year",
        # "academic_year": academic_year,
        "opts": AcademicYear._meta,
    }
    return render(request, "hod/add_academicyear.html", context)


def edit_academicyear(request, pk):
    academic_year = get_object_or_404(AcademicYear, pk=pk)
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
    return render(request, "hod/edit_academicyear.html", context)


def manage_academicyear(request):
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
            return redirect("manage_subject")
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


def manage_student(request):
    search_query = request.GET.get("search", "")
    students = Student.objects.all()

    if search_query:
        students = (
            students.filter(first_name__icontains=search_query)
            | students.filter(last_name__icontains=search_query)
            | students.filter(email__icontains=search_query)
        )

    context = {
        **admin_site.each_context(request),
        "title": "Manage Students",
        "students": students,
        "search_query": search_query,
    }
    return render(request, "hod/manage_student.html", context)


def add_student(request):
    courses = Course.objects.all()
    academic_years = AcademicYear.objects.all()
    occupation_choices = dict(Student.occupation_choice)
    relationship_choices = dict(Student.relationship_choice)

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        middle_name = request.POST.get("middle_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        dob = request.POST.get("dob")
        gender = request.POST.get("gender")
        course_id = request.POST.get("course")
        academic_year_id = request.POST.get("academic_year")
        address = request.POST.get("address")
        father_name = request.POST.get("father_name")
        father_occupation = request.POST.get("father_occupation")
        mother_name = request.POST.get("mother_name")
        mother_occupation = request.POST.get("mother_occupation")
        guardian_name = request.POST.get("guardian_name")
        guardian_number = request.POST.get("guardian_number")
        parents_number = request.POST.get("parents_number")
        relationship_with_student = request.POST.get("relationship_with_student")

        try:
            course = get_object_or_404(Course, id=course_id)
            academic_year = get_object_or_404(AcademicYear, id=academic_year_id)

            Student.objects.create(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                email=email,
                phone=phone,
                dob=dob,
                gender=gender,
                course=course,
                academic_year=academic_year,
                address=address,
                father_name=father_name,
                father_occupation=father_occupation,
                mother_name=mother_name,
                mother_occupation=mother_occupation,
                guardian_name=guardian_name,
                guardian_number=guardian_number,
                parents_number=parents_number,
                relationship_with_student=relationship_with_student,
            )
            messages.success(request, "Student added successfully!")
            return redirect("manage_student")
        except Exception as e:
            messages.error(request, f"Error adding student: {e}")

    context = {
        **admin_site.each_context(request),
        "title": "Add Student",
        "courses": courses,
        "academic_years": academic_years,
        "occupation_choices": occupation_choices.items(),
        "relationship_choices": relationship_choices.items(),
    }
    return render(request, "hod/add_student.html", context)


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    courses = Course.objects.all()
    academic_years = AcademicYear.objects.all()
    occupation_choices = dict(Student.occupation_choice)
    relationship_choices = dict(Student.relationship_choice)

    if request.method == "POST":
        student.first_name = request.POST.get("first_name")
        student.middle_name = request.POST.get("middle_name")
        student.last_name = request.POST.get("last_name")
        student.email = request.POST.get("email")
        student.phone = request.POST.get("phone")
        student.dob = request.POST.get("dob")
        student.gender = request.POST.get("gender")
        student.course = get_object_or_404(Course, id=request.POST.get("course"))
        student.academic_year = get_object_or_404(
            AcademicYear, id=request.POST.get("academic_year")
        )
        student.father_occupation = request.POST.get("father_occupation")
        student.relationship_with_student = request.POST.get(
            "relationship_with_student"
        )

        try:
            student.save()
            messages.success(request, "Student updated successfully!")
            return redirect("manage_student")
        except Exception as e:
            messages.error(request, f"Error updating student: {e}")

    context = {
        **admin_site.each_context(request),
        "title": "Edit Student",
        "student": student,
        "courses": courses,
        "academic_years": academic_years,
        "occupation_choices": occupation_choices.items(),
        "relationship_choices": relationship_choices.items(),
    }
    return render(request, "hod/edit_student.html", context)


def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect("manage_student")


def manage_teacher(request):
    teachers = Teacher.objects.all()
    context = {
        **admin_site.each_context(request),
        "title": "Manage Teachers",
        "teachers": teachers,
    }
    return render(request, "hod/manage_teacher.html", context)


def add_teacher(request):
    if request.method == "POST":
        try:
            Teacher.objects.create(
                first_name=request.POST.get("first_name"),
                middle_name=request.POST.get("middle_name"),
                last_name=request.POST.get("last_name"),
                email=request.POST.get("email"),
                phone=request.POST.get("phone"),
                dob=request.POST.get("dob"),
                gender=request.POST.get("gender"),
                address=request.POST.get("address"),
                # username=request.POST.get("username"),
                # password=request.POST.get("password"),
                qualification=request.POST.get("qualification"),
                specialization_on=request.POST.get("specialization_on"),
                marital_status=request.POST.get("marital_status"),
                date_of_joining=request.POST.get("date_of_joining"),
            )
            messages.success(request, "Teacher added successfully!")
            return redirect("manage_teacher")
        except Exception as e:
            messages.error(request, f"Error adding teacher: {e}")

    context = {
        **admin_site.each_context(request),
        "title": "Add Teacher",
        "qualification_choices": dict(Teacher.qualification_choice).items(),
        "marital_status_choices": dict(Teacher.marital_status_choice).items(),
    }
    return render(request, "hod/add_teacher.html", context)


def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == "POST":
        try:
            teacher.first_name = request.POST.get("first_name")
            teacher.middle_name = request.POST.get("middle_name")
            teacher.last_name = request.POST.get("last_name")
            teacher.email = request.POST.get("email")
            teacher.phone = request.POST.get("phone")
            teacher.dob = request.POST.get("dob")
            teacher.gender = request.POST.get("gender")
            teacher.address = request.POST.get("address")
            teacher.qualification = request.POST.get("qualification")
            teacher.specialization_on = request.POST.get("specialization_on")
            teacher.marital_status = request.POST.get("marital_status")
            teacher.date_of_joining = request.POST.get("date_of_joining")
            teacher.save()

            messages.success(request, "Teacher updated successfully!")
            return redirect("manage_teacher")
        except Exception as e:
            messages.error(request, f"Error updating teacher: {e}")

    context = {
        **admin_site.each_context(request),
        "title": "Edit Teacher",
        "teacher": teacher,
        "qualification_choices": dict(Teacher.qualification_choice).items(),
        "marital_status_choices": dict(Teacher.marital_status_choice).items(),
    }
    return render(request, "hod/edit_teacher.html", context)


def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    teacher.delete()
    messages.success(request, "Teacher deleted successfully!")
    return redirect("manage_teacher")


def student_feedback_message(request):
    feedbacks = FeedbackStudent.objects.all()
    context = {
        **admin_site.each_context(request),
        "title": "Student's Feedback",
        "feedbacks": feedbacks,
    }
    return render(request, "hod/student_feedback.html", context)


@csrf_exempt
def student_feedback_message_reply(request):
    feedback_id = request.POST.get("id")
    feedback_reply = request.POST.get("reply")

    try:
        feedback = FeedbackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def teacher_feedback(request):
    feedbacks = FeedbackTeacher.objects.all()
    context = {
        **admin_site.each_context(request),
        "title": "Staff's Feedback",
        "feedbacks": feedbacks,
    }
    return render(request, "hod/teacher_feedback.html", context)


@csrf_exempt
def teacher_feedback_replied(request):
    feedback_id = request.POST.get("id")
    feedback_message = request.POST.get("message")

    try:
        feedback = FeedbackTeacher.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_message
        feedback.save()
        return HttpResponse("True")
    except Exception:
        return HttpResponse("False")


def student_leave_view(request):
    leaves = LeaveReportStudent.objects.all()
    context = {
        **admin_site.each_context(request),
        "title": "Student Application",
        "leaves": leaves,
    }
    return render(request, "hod/student_leave_view.html", context)


def student_leave_approve(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))


def student_leave_reject(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return HttpResponseRedirect(reverse("student_leave_view"))


def teacher_leave_view(request):
    leaves = LeaveReportTeacher.objects.all()
    context = {
        **admin_site.each_context(request),
        "title": "Teacher Application",
        "leaves": leaves,
    }
    return render(request, "hod/teacher_leave_view.html", context)


def teacher_leave_approve(request, leave_id):
    leave = LeaveReportTeacher.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return HttpResponseRedirect(reverse("teacher_leave_view"))


def teacher_leave_reject(request, leave_id):
    leave = LeaveReportTeacher.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return HttpResponseRedirect(reverse("teacher_leave_view"))


def admin_view_attendance(request):
    subjects = Subject.objects.all()
    academic_years = AcademicYear.objects.all()
    context = {
        **admin_site.each_context(request),
        "subjects": subjects,
        "academic_years": academic_years,
    }
    return render(request, "hod/view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
    # Getting Values from Ajax POST 'Fetch Student'
    subject_id = request.POST.get("subject")
    academic_year = request.POST.get("academic_year_id")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subject.objects.get(id=subject_id)

    academic_model = AcademicYear.objects.get(id=academic_year)

    # students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(
        subject_id=subject_model, academic_year_id=academic_model
    )

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small = {
            "id": attendance_single.id,
            "attendance_date": str(attendance_single.attendance_date),
            "academic_year_id": attendance_single.academic_year_id.id,
        }
        list_data.append(data_small)

    return JsonResponse(
        json.dumps(list_data), content_type="application/json", safe=False
    )


@csrf_exempt
def admin_get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
        data_small = {
            "id": student.student_id.id,
            "name": student.student_id.first_name + " " + student.student_id.last_name,
            "status": student.status,
        }
        list_data.append(data_small)

    return JsonResponse(
        json.dumps(list_data), content_type="application/json", safe=False
    )
