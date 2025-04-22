# Standard library imports
from datetime import timedelta, datetime

# Core Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_GET
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import Group

# Local app imports
from app.models import (
    Staff,
    Student,
    Course,
    CourseTracking,
    Batch,
    StaffLeave,
    Notice,
    FEEDBACK_TYPE_CHOICES,
)


@login_required
def admission_officer_dashboard(request):
    """View to display the admission officer dashboard"""

    # Check if user is in staff and has Admission Officer designation
    if (
        not isinstance(request.user, Staff)
        or request.user.designation != "Admission Officer"
    ):
        messages.error(
            request,
            "You don't have permission to access the admission officer dashboard.",
        )
        return redirect("dashboard")

    # Get the admission officer object
    try:
        admission_officer = request.user
    except Exception as e:
        messages.error(
            request,
            "Admission Officer profile not found. Please contact administrator.",
        )
        return redirect("dashboard")

    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    # Get student statistics and list
    total_students = Student.objects.count()
    active_students = Student.objects.filter(status="Active").count()
    new_students = Student.objects.filter(joining_date__gte=last_month).count()
    students = (
        Student.objects.select_related("course")
        .prefetch_related("batches")
        .all()
        .order_by("-id")
    )  # For the student list

    # Get course statistics and list
    total_courses = Course.objects.count()
    active_courses = Course.objects.filter(is_active=True).count()
    courses = Course.objects.all().order_by("name")  # For the dropdown

    # Get batch statistics and list
    total_batches = Batch.objects.count()
    active_batches = Batch.objects.filter(is_active=True).count()
    batches = Batch.objects.all().order_by("-year")  # For the dropdown

    # Get recent course trackings
    recent_trackings = CourseTracking.objects.select_related(
        "student", "course"
    ).order_by("-created_at")

    # Get leave statistics
    pending_leaves = StaffLeave.objects.filter(
        staff=admission_officer, status=0
    ).count()
    approved_leaves = StaffLeave.objects.filter(
        staff=admission_officer, status=1
    ).count()
    rejected_leaves = StaffLeave.objects.filter(
        staff=admission_officer, status=2
    ).count()

    # Get recent leaves
    recent_leaves = StaffLeave.objects.filter(staff=admission_officer).order_by(
        "-created_at"
    )

    # Get recent notices
    notices = Notice.objects.all().order_by("-created_at")

    # Get feedback types for institute feedback
    feedback_types = FEEDBACK_TYPE_CHOICES

    context = {
        "officer": admission_officer,
        "title": "Admission Officer Dashboard",
        "total_students": total_students,
        "active_students": active_students,
        "new_students": new_students,
        "students": students,  # For the student list
        "total_courses": total_courses,
        "active_courses": active_courses,
        "courses": courses,  # For the dropdown
        "total_batches": total_batches,
        "active_batches": active_batches,
        "batches": batches,  # For the dropdown
        "recent_trackings": recent_trackings,
        "pending_leaves": pending_leaves,
        "approved_leaves": approved_leaves,
        "rejected_leaves": rejected_leaves,
        "recent_leaves": recent_leaves,
        "notices": notices,
        "feedback_types": feedback_types,
    }

    return render(request, "admission_officer/dashboard.html", context)


@login_required
def add_student(request):
    """View to add a new student"""
    if request.method != "POST":
        messages.error(request, "Invalid request method")
        return redirect("admissionOfficerDashboard")

    # Check if user has permission
    if (
        not isinstance(request.user, Staff)
        or request.user.designation != "Admission Officer"
    ):
        messages.error(request, "Permission denied")
        return redirect("admissionOfficerDashboard")

    try:
        # Get form data
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        birth_date = request.POST.get("birth_date")
        course_id = request.POST.get("course")
        current_period = request.POST.get("current_period", 1)
        status = request.POST.get("status", "Active")
        parent_name = request.POST.get("parent_name")
        parent_phone = request.POST.get("parent_phone")
        permanent_address = request.POST.get("permanent_address")
        temporary_address = request.POST.get("temporary_address")
        citizenship_number = request.POST.get("citizenship_number")

        # Get batch ID
        batch_id = request.POST.get("batches")

        # Get photo if uploaded
        photo = request.FILES.get("photo")

        # Validate required fields
        if not all([name, phone, batch_id]):
            messages.error(request, "Name, phone, and batch are required")
            return redirect("admissionOfficerDashboard")

        # Check if student with same phone already exists
        if Student.objects.filter(phone=phone).exists():
            messages.error(request, "Student with this phone number already exists")
            return redirect("admissionOfficerDashboard")

        # Create student object
        student = Student()
        student.name = name
        student.phone = phone
        student.email = email
        student.gender = gender

        # Set birth date if provided
        if birth_date:
            student.birth_date = birth_date

        # Set course if provided
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                student.course = course
                student.current_period = current_period
            except Course.DoesNotExist:
                messages.error(request, "Selected course not found")
                return redirect("admissionOfficerDashboard")

        student.status = status
        student.parent_name = parent_name
        student.parent_phone = parent_phone
        student.permanent_address = permanent_address
        student.temporary_address = temporary_address
        student.citizenship_number = citizenship_number

        # Set photo if uploaded
        if photo:
            student.image = photo

        # Set default password as '123'
        student.set_password("123")

        # Save student
        student.save()

        # Add student to Student group
        student_group, created = Group.objects.get_or_create(name="Student")
        student.groups.add(student_group)

        # Add student to batch
        if batch_id:
            try:
                batch = Batch.objects.get(id=batch_id)
                student.batches.add(batch)
                # Joining date will be set automatically from the batch year in the signal
            except Batch.DoesNotExist:
                messages.error(request, "Selected batch not found")
                # Continue anyway as we've already saved the student

        # Create course tracking if course is assigned
        if course_id:
            try:
                # Use today's date if no joining date yet (should be set by batch signal)
                start_date = student.joining_date or timezone.now().date()

                course_tracking = CourseTracking(
                    student=student,
                    course=course,
                    start_date=start_date,
                    current_period=current_period,
                )
                course_tracking.save()
            except Exception as e:
                print(f"Error creating course tracking: {str(e)}")

        messages.success(
            request, f'Student "{name}" added successfully. Default password is: 123'
        )
        return redirect("admissionOfficerDashboard")

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect("admissionOfficerDashboard")


@login_required
def add_batch(request):
    """View to add a new batch"""
    if request.method != "POST":
        messages.error(request, "Invalid request method")
        return redirect("admissionOfficerDashboard")

    # Check if user has permission
    if (
        not isinstance(request.user, Staff)
        or request.user.designation != "Admission Officer"
    ):
        messages.error(request, "Permission denied")
        return redirect("admissionOfficerDashboard")

    try:
        # Get form data
        name = request.POST.get("name")
        start_date = request.POST.get("start_date")
        is_active = request.POST.get("is_active") == "on"

        # Validate required fields
        if not all([name, start_date]):
            messages.error(request, "Name and start date are required")
            return redirect("admissionOfficerDashboard")

        # Create batch
        batch = Batch()
        batch.name = name
        batch.year = start_date  # Use start_date for the year field
        batch.is_active = is_active
        batch.save()

        messages.success(request, f'Batch "{name}" added successfully')
        return redirect("admissionOfficerDashboard")

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect("admissionOfficerDashboard")


@login_required
def add_course(request):
    """View to add a new course"""
    if request.method != "POST":
        messages.error(request, "Invalid request method")
        return redirect("admissionOfficerDashboard")

    # Check if user has permission
    if (
        not isinstance(request.user, Staff)
        or request.user.designation != "Admission Officer"
    ):
        messages.error(request, "Permission denied")
        return redirect("admissionOfficerDashboard")

    try:
        # Get form data
        name = request.POST.get("name")
        code = request.POST.get("code", "")
        duration_type = request.POST.get("duration_type")
        duration = request.POST.get("duration")
        description = request.POST.get("description", "")
        is_active = request.POST.get("is_active") == "on"

        # Validate required fields
        if not all([name, duration_type, duration]):
            messages.error(request, "Name, duration type, and duration are required")
            return redirect("admissionOfficerDashboard")

        # Create course
        course = Course()
        course.name = name
        course.code = code
        course.duration_type = duration_type
        course.duration = duration
        course.description = description
        course.is_active = is_active
        course.save()

        messages.success(request, f'Course "{name}" added successfully')
        return redirect("admissionOfficerDashboard")

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect("admissionOfficerDashboard")


@login_required
def add_course_tracking(request):
    """View to add course tracking for a student"""
    if request.method != "POST":
        messages.error(request, "Invalid request method")
        return redirect("admissionOfficerDashboard")

    # Check if user has permission
    if (
        not isinstance(request.user, Staff)
        or request.user.designation != "Admission Officer"
    ):
        messages.error(request, "Permission denied")
        return redirect("admissionOfficerDashboard")

    try:
        # Get form data
        student_id = request.POST.get("student")
        course_id = request.POST.get("course")
        start_date = request.POST.get("start_date")
        expected_end_date = request.POST.get("expected_end_date")
        current_period = request.POST.get("current_period", 1)
        progress_status = request.POST.get("progress_status", "In Progress")
        notes = request.POST.get("notes")

        # Validate required fields
        if not student_id or not course_id:
            messages.error(request, "Student and course are required")
            return redirect("admissionOfficerDashboard")

        # Check if student exists
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            messages.error(request, "Student not found")
            return redirect("admissionOfficerDashboard")

        # Check if course exists
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            messages.error(request, "Course not found")
            return redirect("admissionOfficerDashboard")

        # Check if tracking already exists
        if CourseTracking.objects.filter(student=student, course=course).exists():
            messages.error(request, "Student is already enrolled in this course")
            return redirect("admissionOfficerDashboard")

        # Create course tracking object
        tracking = CourseTracking()
        tracking.student = student
        tracking.course = course

        # Set dates if provided
        if start_date:
            tracking.start_date = start_date
        if expected_end_date:
            tracking.expected_end_date = expected_end_date

        tracking.current_period = int(current_period)
        tracking.progress_status = progress_status
        tracking.notes = notes

        # Save tracking
        tracking.save()

        messages.success(
            request,
            f'Course tracking added for student "{student.name}" in course "{course.name}"',
        )
        return redirect("admissionOfficerDashboard")

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect("admissionOfficerDashboard")


@login_required
def get_courses(request):
    """View to get courses for dropdowns"""
    try:
        courses = Course.objects.all().order_by("name")
        course_data = [
            {"id": course.id, "name": course.name, "code": course.code}
            for course in courses
        ]

        return JsonResponse({"success": True, "courses": course_data})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@login_required
def get_batches(request):
    """View to get batches for dropdowns"""
    try:
        batches = Batch.objects.all().order_by("-year")
        batch_data = []

        for batch in batches:
            batch_data.append(
                {
                    "id": batch.id,
                    "name": batch.name,
                    "year": batch.year.year if batch.year else None,
                    "display_name": f"{batch.name} ({batch.year.year if batch.year else 'No year'})",
                }
            )

        return JsonResponse({"success": True, "batches": batch_data})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@login_required
def get_students(request):
    """View to get students for dropdowns"""
    try:
        students = Student.objects.all()
        student_data = [
            {"id": student.id, "name": student.name, "phone": student.phone}
            for student in students
        ]

        return JsonResponse({"success": True, "students": student_data})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@login_required
def get_student(request, student_id):
    """View to get a student's details by ID"""
    # Check if user has permission
    if (
        not isinstance(request.user, Staff)
        or request.user.designation != "Admission Officer"
    ):
        return JsonResponse(
            {"success": False, "message": "Permission denied"}, status=403
        )

    try:
        # Get student with related data
        student = (
            Student.objects.select_related("course")
            .prefetch_related("batches")
            .get(id=student_id)
        )

        # Build batches data
        batches = []
        for batch in student.batches.all():
            batches.append(
                {
                    "id": batch.id,
                    "name": batch.name,
                    "year": batch.year.year if batch.year else None,
                }
            )

        # Build student data
        student_data = {
            "id": student.id,
            "name": student.name,
            "phone": student.phone,
            "email": student.email,
            "gender": student.gender,
            "birth_date": student.birth_date.strftime("%Y-%m-%d")
            if student.birth_date
            else None,
            "status": student.status,
            "parent_name": student.parent_name,
            "parent_phone": student.parent_phone,
            "permanent_address": student.permanent_address,
            "temporary_address": student.temporary_address,
            "citizenship_number": student.citizenship_no,
            "current_period": student.current_period,
            "joining_date": student.joining_date.strftime("%Y-%m-%d")
            if student.joining_date
            else None,
            "image": student.image.url if student.image else None,
            "course": {"id": student.course.id, "name": student.course.name}
            if student.course
            else None,
            "batches": batches,
        }

        return JsonResponse({"success": True, "student": student_data})
    except Student.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Student not found"}, status=404
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@login_required
def edit_student(request):
    """View to edit a student's details"""
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )

    # Check if user has permission
    if (
        not isinstance(request.user, Staff)
        or request.user.designation != "Admission Officer"
    ):
        return JsonResponse(
            {"success": False, "message": "Permission denied"}, status=403
        )

    try:
        # Get student ID from form data
        student_id = request.POST.get("student_id")
        if not student_id:
            return JsonResponse(
                {"success": False, "message": "Student ID is required"}, status=400
            )

        # Get student object
        student = get_object_or_404(Student, id=student_id)

        # Update student fields
        student.name = request.POST.get("name", student.name)
        student.phone = request.POST.get("phone", student.phone)
        student.email = request.POST.get("email", student.email)
        student.gender = request.POST.get("gender", student.gender)

        # Handle birth date
        birth_date = request.POST.get("birth_date")
        if birth_date:
            student.birth_date = birth_date

        # Handle course
        course_id = request.POST.get("course")
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                student.course = course
            except Course.DoesNotExist:
                pass

        # Handle status
        status = request.POST.get("status")
        if status:
            student.status = status

        # Handle parent info
        student.parent_name = request.POST.get("parent_name", student.parent_name)
        student.parent_phone = request.POST.get("parent_phone", student.parent_phone)

        # Handle address
        student.permanent_address = request.POST.get(
            "permanent_address", student.permanent_address
        )

        # Handle citizenship
        student.citizenship_no = request.POST.get(
            "citizenship_number", student.citizenship_no
        )

        # Save student
        student.save()

        # Handle batch
        batch_id = request.POST.get("batches")
        if batch_id:
            try:
                batch = Batch.objects.get(id=batch_id)
                # Clear existing batches and add the new one
                student.batches.clear()
                student.batches.add(batch)
            except Batch.DoesNotExist:
                pass

        return JsonResponse(
            {"success": True, "message": "Student updated successfully"}
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@login_required
def get_course_tracking(request, tracking_id):
    """View to get a course tracking's details by ID"""
    # Check if user has permission
    if (
        not isinstance(request.user, Staff)
        or request.user.designation != "Admission Officer"
    ):
        return JsonResponse(
            {"success": False, "message": "Permission denied"}, status=403
        )

    try:
        # Get tracking with related data
        tracking = CourseTracking.objects.select_related("student", "course").get(
            id=tracking_id
        )

        # Build tracking data
        tracking_data = {
            "id": tracking.id,
            "student": {"id": tracking.student.id, "name": tracking.student.name},
            "course": {"id": tracking.course.id, "name": tracking.course.name},
            "start_date": tracking.start_date.strftime("%Y-%m-%d"),
            "expected_end_date": tracking.expected_end_date.strftime("%Y-%m-%d")
            if tracking.expected_end_date
            else None,
            "completion_percentage": tracking.completion_percentage,
            "progress_status": tracking.progress_status,
            "current_period": tracking.current_period,
            "notes": tracking.notes,
            "current_period_display": tracking.current_period_display,
        }

        return JsonResponse({"success": True, "tracking": tracking_data})
    except CourseTracking.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Course tracking not found"}, status=404
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@login_required
def edit_course_tracking(request):
    """View to edit a course tracking"""
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )

    # Check if user has permission
    if (
        not isinstance(request.user, Staff)
        or request.user.designation != "Admission Officer"
    ):
        return JsonResponse(
            {"success": False, "message": "Permission denied"}, status=403
        )

    try:
        # Get tracking ID from form data
        tracking_id = request.POST.get("tracking_id")
        if not tracking_id:
            return JsonResponse(
                {"success": False, "message": "Tracking ID is required"}, status=400
            )

        # Get tracking object
        tracking = get_object_or_404(CourseTracking, id=tracking_id)

        # Update tracking fields
        start_date = request.POST.get("start_date")
        if start_date:
            tracking.start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

        expected_end_date = request.POST.get("expected_end_date")
        if expected_end_date:
            tracking.expected_end_date = datetime.strptime(expected_end_date, "%Y-%m-%d").date()

        current_period = request.POST.get("current_period")
        if current_period:
            tracking.current_period = int(current_period)

        progress_status = request.POST.get("progress_status")
        if progress_status:
            tracking.progress_status = progress_status

        completion_percentage = request.POST.get("completion_percentage")
        if completion_percentage:
            tracking.completion_percentage = int(completion_percentage)

        notes = request.POST.get("notes")
        if notes is not None:  # Allow empty notes
            tracking.notes = notes

        # Save tracking
        tracking.save()

        return JsonResponse(
            {"success": True, "message": "Course tracking updated successfully"}
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
