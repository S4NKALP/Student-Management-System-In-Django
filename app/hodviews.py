from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta, time
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os

from app.firebase import send_push_notification, FCMDevice
from app.utils import (
    handle_file_upload,
    cleanup_failed_upload,
    FileUploadError,
    ALLOWED_DOCUMENT_TYPES,
    MAX_DOCUMENT_SIZE
)

from app.models import (
    Staff,
    Student,
    Course,
    Subject,
    Routine,
    Attendance,
    AttendanceRecord,
    StudentFeedback,
    CourseTracking,
    TeacherParentMeeting,
    Batch,
    Parent,
    Notice,
)


@login_required
def hod_dashboard(request):
    """HOD dashboard view showing department overview and management options"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            messages.error(request, "Only HODs can access this dashboard.")
            return redirect("hodDashboard")

        # Get the HOD's department (course)
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            messages.error(request, "You are not assigned as HOD of any department.")
            return redirect("hodDashboard")

        course = hod.course

        # Get department statistics
        total_students = Student.objects.filter(course=course).count()
        total_staff = Staff.objects.filter(course=course).count()
        total_subjects = Subject.objects.filter(course=course).count()

        # Get all subjects for the course
        subjects = Subject.objects.filter(course=course).order_by('period_or_year', 'name')

        # Get routines to find teachers for each subject
        routines = Routine.objects.filter(course=course, is_active=True).select_related(
            "subject", "teacher"
        )

        # Create a mapping of subject_id to teacher
        teacher_map = {}
        for routine in routines:
            teacher_map[routine.subject_id] = routine.teacher

        # Get all teachers who teach in this course through active routines
        staff = Staff.objects.filter(
            id__in=routines.values_list('teacher_id', flat=True)
        ).prefetch_related(
            'routine_set',
            'routine_set__subject'
        ).distinct()

        # Filter routines for each staff member to only show subjects from this course
        for staff_member in staff:
            staff_member.filtered_subjects = Subject.objects.filter(
                course=course,
                id__in=staff_member.routine_set.filter(is_active=True).values_list('subject_id', flat=True)
            )

        # Get today's classes and their attendance
        today = timezone.now().date()
        today_classes = Routine.objects.filter(
            course=course,
            is_active=True
        ).select_related("subject", "teacher")

        # Get attendance for today's classes
        today_attendance = Attendance.objects.filter(
            routine__course=course,
            date=today
        ).select_related("routine")

        # Create a dictionary of routine_id to attendance
        attendance_map = {att.routine_id: att for att in today_attendance}

        # Attach attendance to each class
        for class_obj in today_classes:
            class_obj.attendance = attendance_map.get(class_obj.id)

        # Get all student progress records for display in the progress section
        student_progress_all = (
            CourseTracking.objects.filter(student__course=course)
            .select_related("student")
            .order_by("-completion_percentage")
        )
        
        # Calculate progress metrics
        avg_completion = student_progress_all.aggregate(Avg('completion_percentage'))['completion_percentage__avg'] or 0
        avg_completion = round(avg_completion, 1)
        students_on_track = student_progress_all.filter(completion_percentage__gte=75).count()
        students_at_risk = student_progress_all.filter(completion_percentage__lt=40).count()
        
        # For the dashboard overview, still show just top 5
        student_progress = student_progress_all[:5]

        # Get all meetings
        meetings = TeacherParentMeeting.objects.all().order_by("-meeting_date", "-meeting_time")

        # Get recent feedback
        recent_feedback = (
            StudentFeedback.objects.filter(student__course=course)
            .select_related("student", "teacher")
            .order_by("-created_at")[:5]
        )

        # Get all students in the course
        students = Student.objects.filter(course=course).order_by('name')

        # Get all active batches
        batches = Batch.objects.filter(is_active=True).order_by('-year')
        
        # Get notices
        notices = Notice.objects.all().order_by('-created_at')

        context = {
            "title": "HOD Dashboard",
            "hod": hod,
            "course": course,
            "total_students": total_students,
            "total_staff": total_staff,
            "total_subjects": total_subjects,
            "today_classes": today_classes,
            "student_progress": student_progress,
            "student_progress_all": student_progress_all,  # All student progress records
            "avg_completion": avg_completion,
            "students_on_track": students_on_track,
            "students_at_risk": students_at_risk,
            "meetings": meetings,  # Changed from upcoming_meetings to all meetings
            "recent_feedback": recent_feedback,
            "subjects": subjects,
            "staff": staff,
            "students": students,
            "batches": batches,
            "notices": notices,
            "class_routines": routines,  # Add routines to the context
        }

        return render(request, "hod/dashboard.html", context)

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("hodDashboard")

@login_required
def add_subject(request):
    if request.method == "POST":
        try:
            name = request.POST.get("name")
            code = request.POST.get("code")
            period_or_year = request.POST.get("period_or_year")
            syllabus_pdf = request.FILES.get("syllabus_pdf")

            if not name or not period_or_year:
                return JsonResponse(
                    {"success": False, "error": "Name and period/year are required"}
                )

            # Handle syllabus PDF upload if provided
            syllabus_path = None
            if syllabus_pdf:
                try:
                    syllabus_path = handle_file_upload(
                        syllabus_pdf,
                        "subject_syllabus",
                        ALLOWED_DOCUMENT_TYPES,
                        MAX_DOCUMENT_SIZE
                    )
                except FileUploadError as e:
                    return JsonResponse({"success": False, "error": str(e)})

            try:
                # Create subject with uploaded syllabus
                subject = Subject.objects.create(
                    name=name,
                    code=code,
                    period_or_year=period_or_year,
                    syllabus_pdf=syllabus_path
                )

                return JsonResponse(
                    {"success": True, "message": "Subject added successfully"}
                )
            except Exception as e:
                # Clean up uploaded file if database operation fails
                if syllabus_path:
                    cleanup_failed_upload(syllabus_path)
                return JsonResponse({"success": False, "error": str(e)})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})

@login_required
def view_subject(request, subject_id):
    """View details of a specific subject"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can view subject details."})

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})

        # Get the subject and ensure it belongs to the HOD's course
        subject = get_object_or_404(Subject, id=subject_id, course=hod.course)
        
        # Get the assigned teacher from routine if any
        teacher = None
        routine = Routine.objects.filter(subject=subject, is_active=True).first()
        if routine:
            teacher = routine.teacher

        # Prepare response data
        response_data = {
            "success": True,
            "subject": {
                "id": subject.id,
                "name": subject.name,
                "code": subject.code or "N/A",
                "course": {
                    "id": subject.course.id,
                    "name": subject.course.name,
                    "duration_type": subject.course.duration_type,
                    "duration": subject.course.duration
                },
                "period_or_year": subject.period_or_year,
                "teacher": {
                    "id": teacher.id,
                    "name": teacher.name
                } if teacher else None,
                "syllabus_pdf": subject.syllabus_pdf.url if subject.syllabus_pdf else None
            }
        }
        
        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def edit_subject(request):
    if request.method == "POST":
        try:
            subject_id = request.POST.get("subject_id")
            name = request.POST.get("name")
            code = request.POST.get("code")
            period_or_year = request.POST.get("period_or_year")
            syllabus_pdf = request.FILES.get("syllabus_pdf")

            if not subject_id or not name or not period_or_year:
                return JsonResponse(
                    {"success": False, "error": "Subject ID, name and period/year are required"}
                )

            try:
                subject = Subject.objects.get(id=subject_id)
            except Subject.DoesNotExist:
                return JsonResponse({"success": False, "error": "Subject not found"})

            # Handle syllabus PDF upload if provided
            syllabus_path = None
            if syllabus_pdf:
                try:
                    syllabus_path = handle_file_upload(
                        syllabus_pdf,
                        "subject_syllabus",
                        ALLOWED_DOCUMENT_TYPES,
                        MAX_DOCUMENT_SIZE
                    )
                except FileUploadError as e:
                    return JsonResponse({"success": False, "error": str(e)})

            try:
                # Update subject fields
                subject.name = name
                subject.code = code
                subject.period_or_year = period_or_year

                # Update syllabus if new one was uploaded
                if syllabus_path:
                    # Delete old syllabus if exists
                    if subject.syllabus_pdf:
                        if os.path.isfile(subject.syllabus_pdf.path):
                            os.remove(subject.syllabus_pdf.path)
                    subject.syllabus_pdf = syllabus_path

                subject.save()

                return JsonResponse(
                    {"success": True, "message": "Subject updated successfully"}
                )
            except Exception as e:
                # Clean up uploaded file if database operation fails
                if syllabus_path:
                    cleanup_failed_upload(syllabus_path)
                return JsonResponse({"success": False, "error": str(e)})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})

@login_required(login_url='login')
def delete_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        # Check if the subject is being used in any routines
        if Routine.objects.filter(subject=subject).exists():
            messages.error(request, 'Cannot delete subject as it is being used in routines.')
            return redirect('hodDashboard')
        
        # Delete the subject
        subject.delete()
        messages.success(request, 'Subject deleted successfully.')
        return redirect('hodDashboard')
    except Subject.DoesNotExist:
        messages.error(request, 'Subject not found.')
        return redirect('hodDashboard')
    except Exception as e:
        messages.error(request, f'Error deleting subject: {str(e)}')
        return redirect('hodDashboard')

@login_required
def add_staff(request):
    """Add a new staff member"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can add staff members."})

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})

        course = hod.course

        if request.method == "POST":
            # Get form data
            name = request.POST.get("name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            gender = request.POST.get("gender")
            birth_date = request.POST.get("birth_date")
            temporary_address = request.POST.get("temporary_address")
            permanent_address = request.POST.get("permanent_address")
            marital_status = request.POST.get("marital_status")
            citizenship_no = request.POST.get("citizenship_no")
            subject_ids = request.POST.getlist("subjects[]")  # Updated to match the form field name

            # Validate required fields
            if not name or not phone:
                return JsonResponse({"success": False, "message": "Name and phone are required fields."})

            if not subject_ids:
                return JsonResponse({"success": False, "message": "Please assign at least one subject."})

            # Check if phone number already exists
            if Staff.objects.filter(phone=phone).exists():
                return JsonResponse({"success": False, "message": "Phone number already exists."})

            # Create the staff member with default password and current date as joining date
            staff = Staff(
                name=name,
                email=email,
                phone=phone,
                gender=gender,
                birth_date=birth_date if birth_date else None,
                temporary_address=temporary_address,
                permanent_address=permanent_address,
                marital_status=marital_status,
                citizenship_no=citizenship_no,
                password=make_password("123"),  # Default password
                is_active=True,
                joining_date=timezone.now().date(),  # Set joining date to current date
                course=course,  # Assign to HOD's course
                designation="Teacher"  # Set designation as Teacher
            )

            staff.save()

            # Add to Teacher group
            try:
                teacher_group = Group.objects.get(name="Teacher")
                staff.groups.add(teacher_group)
            except Group.DoesNotExist:
                # Create Teacher group if it doesn't exist
                teacher_group = Group.objects.create(name="Teacher")
                staff.groups.add(teacher_group)

            # Create routines for assigned subjects with default time slots
            default_start_time = time(10, 0)  # 10:00 AM
            default_end_time = time(11, 0)    # 11:00 AM

            for subject_id in subject_ids:
                try:
                    subject = Subject.objects.get(id=subject_id, course=course)
                    Routine.objects.create(
                        teacher=staff,
                        subject=subject,
                        course=course,
                        period_or_year=subject.period_or_year,
                        start_time=default_start_time,
                        end_time=default_end_time,
                        is_active=True
                    )
                except Subject.DoesNotExist:
                    continue

            return JsonResponse({"success": True, "message": "Staff member added successfully."})

        return JsonResponse({"success": False, "message": "Invalid request method."})

    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def view_staff(request, staff_id):
    """View details of a staff member"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can view staff details."})

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})

        course = hod.course

        # Get the staff member and ensure they belong to the HOD's course
        staff = get_object_or_404(Staff, id=staff_id)

        # Get only the subjects from this course taught by this staff member
        subjects = Subject.objects.filter(
            course=course,
            id__in=Routine.objects.filter(teacher=staff, is_active=True).values_list('subject_id', flat=True)
        )

        # Prepare response data with all staff fields
        response_data = {
            "success": True,
            "staff": {
                "id": staff.id,
                "name": staff.name,
                "email": staff.email,
                "phone": staff.phone,
                "designation": staff.designation,
                "gender": staff.gender,
                "birth_date": staff.birth_date.strftime("%Y-%m-%d") if staff.birth_date else None,
                "temporary_address": staff.temporary_address,
                "permanent_address": staff.permanent_address,
                "marital_status": staff.marital_status,
                "parent_name": staff.parent_name,
                "parent_phone": staff.parent_phone,
                "citizenship_no": staff.citizenship_no,
                "passport": staff.passport,
                "image": staff.image.url if staff.image else None,
                "joining_date": staff.joining_date.strftime("%Y-%m-%d") if staff.joining_date else None,
                "is_active": staff.is_active,
                "subjects": [{"id": subject.id, "name": subject.name} for subject in subjects]
            }
        }
        
        return JsonResponse(response_data)

    except Exception as e:
        print(f"Error in view_staff: {str(e)}")  # Debug log
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def edit_staff(request, staff_id):
    """Edit an existing staff member"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can edit staff members."})

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})

        # Get the staff member and ensure they belong to the HOD's course
        staff = get_object_or_404(Staff, id=staff_id)

        if request.method == "POST":
            # Get form data
            name = request.POST.get("name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            is_active = request.POST.get("is_active") == "true"

            # Validate required fields
            if not name or not phone:
                return JsonResponse({"success": False, "message": "Name and phone are required."})

            # Check if phone number already exists for other staff members
            if Staff.objects.filter(phone=phone).exclude(id=staff_id).exists():
                return JsonResponse({"success": False, "message": "Phone number already exists."})

            # Update staff details
            staff.name = name
            staff.email = email
            staff.phone = phone
            staff.is_active = is_active

            # Handle profile picture upload if provided
            if request.FILES.get('image'):
                staff.image = request.FILES['image']

            staff.save()

            return JsonResponse({"success": True, "message": "Staff member updated successfully."})

        return JsonResponse({"success": False, "message": "Invalid request method."})

    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def delete_staff(request, staff_id):
    """Delete a staff member"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            messages.error(request, "Only Head of Department can delete staff members")
            return redirect("hodDashboard")

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            messages.error(request, "You are not assigned as HOD of any department")
            return redirect("hodDashboard")

        # Get the staff member
        staff = get_object_or_404(Staff, id=staff_id)
        
        # Check if staff belongs to HOD's course
        if staff.course != hod.course:
            messages.error(request, "You can only delete staff members from your department")
            return redirect("hodDashboard")

        # Delete all routines associated with the staff
        staff_routines = Routine.objects.filter(teacher=staff)
        staff_routines.delete()

        # Store staff name for the success message
        staff_name = staff.name

        # Delete the staff member
        staff.delete()

        # Add success message
        messages.success(request, f'Staff member {staff_name} has been deleted successfully')
        
        # Redirect back to dashboard
        return redirect("hodDashboard")

    except Staff.DoesNotExist:
        messages.error(request, "Staff member not found")
        return redirect("hodDashboard")
    except Exception as e:
        messages.error(request, "An error occurred while deleting the staff member")
        return redirect("hodDashboard")

@login_required
def add_student(request):
    """Add a new student to the HOD's course"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can add students."})

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})

        course = hod.course

        if request.method == "POST":
            # Get form data
            name = request.POST.get("name")
            phone = request.POST.get("phone")
            email = request.POST.get("email")
            gender = request.POST.get("gender")
            birth_date = request.POST.get("birth_date")
            batch_id = request.POST.get("batch")
            status = request.POST.get("status")
            temporary_address = request.POST.get("temporary_address")
            permanent_address = request.POST.get("permanent_address")
            parent_name = request.POST.get("parent_name")
            parent_phone = request.POST.get("parent_phone")
            parent_address = request.POST.get("parent_address")
            citizenship_no = request.POST.get("citizenship_no")

            # Validate required fields
            if not name or not phone or not batch_id or not status or not parent_phone:
                return JsonResponse({"success": False, "message": "Name, phone, batch, status, and parent phone are required."})

            # Check if phone already exists
            if Student.objects.filter(phone=phone).exists():
                return JsonResponse({"success": False, "message": "Phone number already exists."})

            try:
                # Get the batch
                batch = Batch.objects.get(id=batch_id)
                
                # Create or get parent account
                try:
                    parent = Parent.objects.get(phone=parent_phone)
                except Parent.DoesNotExist:
                    parent = Parent(
                        name=parent_name,
                        phone=parent_phone,
                        address=parent_address,
                        password=make_password("123")  # Default password
                    )
                    parent.save()
                    
                    # Add parent to Parent group
                    try:
                        parent_group = Group.objects.get(name="Parent")
                        parent.groups.add(parent_group)
                    except Group.DoesNotExist:
                        parent_group = Group.objects.create(name="Parent")
                        parent.groups.add(parent_group)
                
                # Create the student
                student = Student(
                    name=name,
                    phone=phone,
                    email=email,
                    gender=gender,
                    birth_date=birth_date if birth_date else None,
                    joining_date=batch.year if batch.year else timezone.now().date(),
                    temporary_address=temporary_address,
                    permanent_address=permanent_address,
                    parent_name=parent_name,
                    parent_phone=parent_phone,
                    citizenship_no=citizenship_no,
                    course=course,
                    status=status,
                    is_active=True,
                    password=make_password("123")  # Set default password to "123"
                )

                # Save the student first to get an ID
                student.save()

                # Add student to batch
                student.batches.add(batch)

                # Add student to Student group
                try:
                    student_group = Group.objects.get(name="Student")
                    student.groups.add(student_group)
                except Group.DoesNotExist:
                    student_group = Group.objects.create(name="Student")
                    student.groups.add(student_group)

                # Associate student with parent
                parent.students.add(student)

                return JsonResponse({
                    "success": True, 
                    "message": "Student added successfully. Default password is: 123"
                })

            except Batch.DoesNotExist:
                return JsonResponse({
                    "success": False, 
                    "message": "Selected batch does not exist."
                })
            except Exception as e:
                return JsonResponse({
                    "success": False, 
                    "message": f"Error creating student: {str(e)}"
                })

        return JsonResponse({"success": False, "message": "Invalid request method."})

    except Exception as e:
        return JsonResponse({
            "success": False, 
            "message": f"An error occurred: {str(e)}"
        })

@login_required
def get_student(request, student_id):
    """Get student details"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can view student details."})

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})

        # Get the student and ensure they belong to the HOD's course
        student = get_object_or_404(Student, id=student_id)
        
        # Prepare response data
        response_data = {
            "success": True,
            "student": {
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "phone": student.phone,
                "gender": student.gender,
                "birth_date": student.birth_date.strftime("%Y-%m-%d") if student.birth_date else None,
                "joining_date": student.joining_date.strftime("%Y-%m-%d") if student.joining_date else None,
                "temporary_address": student.temporary_address,
                "permanent_address": student.permanent_address,
                "parent_name": student.parent_name,
                "parent_phone": student.parent_phone,
                "citizenship_no": student.citizenship_no,
                "image": student.image.url if student.image else None,
                "course_name": student.course.name if student.course else None,
                "current_period": student.current_period,
                "is_active": student.is_active
            }
        }
        
        return JsonResponse(response_data)

    except Exception as e:
        print(f"Error in get_student: {str(e)}")  # Debug log
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def edit_student(request, student_id):
    """Edit an existing student"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can edit students."})

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})

        # Get the student and ensure they belong to the HOD's course
        student = get_object_or_404(Student, id=student_id, course=hod.course)

        if request.method == "POST":
            # Get form data
            name = request.POST.get("name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            gender = request.POST.get("gender")
            birth_date = request.POST.get("birth_date")
            batch_id = request.POST.get("batch")
            temporary_address = request.POST.get("temporary_address")
            permanent_address = request.POST.get("permanent_address")
            parent_name = request.POST.get("parent_name")
            parent_phone = request.POST.get("parent_phone")
            citizenship_no = request.POST.get("citizenship_no")

            # Validate required fields
            if not name or not phone:
                return JsonResponse({"success": False, "message": "Name and phone are required fields."})

            # Check if email or phone already exists for other students
            if email and Student.objects.filter(email=email).exclude(id=student_id).exists():
                return JsonResponse({"success": False, "message": "Email already exists."})
            if Student.objects.filter(phone=phone).exclude(id=student_id).exists():
                return JsonResponse({"success": False, "message": "Phone number already exists."})

            # Update student details
            student.name = name
            student.email = email
            student.phone = phone
            student.gender = gender
            student.birth_date = birth_date if birth_date else None
            student.temporary_address = temporary_address
            student.permanent_address = permanent_address
            student.parent_name = parent_name
            student.parent_phone = parent_phone
            student.citizenship_no = citizenship_no

            # Update batch and set joining date based on batch if provided
            if batch_id:
                try:
                    batch = Batch.objects.get(id=batch_id)
                    # Clear existing batches and add the new one
                    student.batches.clear()
                    student.batches.add(batch)
                    # Set joining date based on batch year
                    student.joining_date = batch.year if batch.year else timezone.now().date()
                except Batch.DoesNotExist:
                    pass

            # Handle profile picture upload if provided
            if request.FILES.get('image'):
                student.image = request.FILES['image']

            student.save()

            return JsonResponse({"success": True, "message": "Student updated successfully."})

        return JsonResponse({"success": False, "message": "Invalid request method."})

    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def delete_student(request, student_id):
    """Delete a student"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            messages.error(request, "Only HODs can delete students.")
            return redirect('hodDashboard')

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            messages.error(request, "You are not assigned as HOD of any department.")
            return redirect('hodDashboard')

        # Get the student and ensure they belong to the HOD's course
        student = get_object_or_404(Student, id=student_id, course=hod.course)

        # Check if student has any attendance records
        if AttendanceRecord.objects.filter(student=student).exists():
            messages.error(request, "Cannot delete student as they have attendance records.")
            return redirect('hodDashboard')

        # Delete the student
        student.delete()
        messages.success(request, "Student deleted successfully.")
        return redirect('hodDashboard')

    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('hodDashboard')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('hodDashboard')

@login_required
def add_notice(request):
    """Add a new notice and notify students and parents"""
    try:
        # Check if user is HOD
        if not request.user.groups.filter(name="HOD").exists():
            messages.error(request, "Only HODs can add notices.")
            return redirect('hodDashboard')
        
        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            messages.error(request, "You are not assigned as HOD of any department.")
            return redirect('hodDashboard')
        
        course = hod.course
        
        if request.method == "POST":
            title = request.POST.get("title")
            message = request.POST.get("message")
            
            # Validate required fields
            if not title:
                messages.error(request, "Title is required.")
                return redirect('hodDashboard')
            
            # Create notice
            notice = Notice(
                title=title,
                message=message
            )
            
            # Handle image if provided
            if request.FILES.get("image"):
                notice.image = request.FILES.get("image")
            
            # Handle file attachment if provided
            if request.FILES.get("file"):
                notice.file = request.FILES.get("file")
            
            notice.save()
            
            # Get students from the HOD's course with FCM tokens
            students = Student.objects.filter(course=course, fcm_token__isnull=False)
            
            # Get parents of these students with FCM tokens
            student_ids = students.values_list('id', flat=True)
            parents = Parent.objects.filter(students__in=student_ids, fcm_token__isnull=False).distinct()
            
            # Collect all FCM tokens
            tokens = []
            
            # Add student tokens
            student_tokens = students.values_list('fcm_token', flat=True)
            tokens.extend(student_tokens)
            
            # Add parent tokens
            parent_tokens = parents.values_list('fcm_token', flat=True)
            tokens.extend(parent_tokens)
            
            # Remove any empty or null tokens
            tokens = [token for token in tokens if token]
            
            # Send push notifications if we have any tokens
            if tokens:
                try:
                    # Send notification to all tokens at once
                    success_count, failure_count, failed_tokens = send_push_notification(
                        "New Notice: {title}",
                        message[:100] + "..." if len(message) > 100 else message,
                        tokens
                    )
                    
                    if failure_count > 0:
                        print(f"Failed to send notifications to {failure_count} devices")
                        print(f"Failed tokens: {failed_tokens}")
                except Exception as e:
                    print(f"Error sending notifications: {str(e)}")
            
            messages.success(request, "Notice added successfully and notifications sent.")
            return redirect('hodDashboard')
        
        return render(request, 'hod/dashboard.html')
        
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('hodDashboard')

@login_required
def view_notice(request, notice_id):
    """View notice details"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            messages.error(request, "Access denied.")
            return redirect('hodDashboard')
        
        # Get notice
        notice = get_object_or_404(Notice, id=notice_id)
        
        context = {
            "notice": notice,
            "title": "View Notice"
        }
        
        return render(request, 'hod/view_notice.html', context)
        
    except Notice.DoesNotExist:
        messages.error(request, "Notice not found.")
        return redirect('hodDashboard')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('hodDashboard')

@login_required
def delete_notice(request, notice_id):
    """Delete a notice"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            messages.error(request, "Only HODs can delete notices.")
            return redirect('hodDashboard')
        
        # Get notice
        notice = get_object_or_404(Notice, id=notice_id)
        
        # Delete notice
        notice.delete()
        
        messages.success(request, "Notice deleted successfully.")
        return redirect('hodDashboard')
        
    except Notice.DoesNotExist:
        messages.error(request, "Notice not found.")
        return redirect('hodDashboard')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('hodDashboard')

@login_required
def add_meeting(request):
    """Add a new teacher-parent meeting and notify relevant users"""
    try:
        # Check if user is HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can schedule meetings."})
        
        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})
        
        course = hod.course
        
        if request.method == "POST":
            meeting_date = request.POST.get("meeting_date")
            meeting_time = request.POST.get("meeting_time")
            duration = request.POST.get("duration")
            agenda = request.POST.get("agenda", "")
            is_online = request.POST.get("is_online") == "true"
            meeting_link = request.POST.get("meeting_link", "") or ""  # Ensure never NULL
            
            # Validate required fields
            if not all([meeting_date, meeting_time, duration]):
                return JsonResponse({"success": False, "message": "Date, time and duration are required."})
            
            # Create meeting
            meeting = TeacherParentMeeting(
                meeting_date=meeting_date,
                meeting_time=meeting_time,
                duration=duration,
                agenda=agenda,
                is_online=is_online,
                meeting_link=meeting_link,  # Now guaranteed to be at least empty string
                status="scheduled"
            )
            
            meeting.save()
            
            # Get students from the HOD's course with FCM tokens
            students = Student.objects.filter(course=course, fcm_token__isnull=False)
            
            # Get parents of these students with FCM tokens
            student_ids = students.values_list('id', flat=True)
            parents = Parent.objects.filter(students__in=student_ids, fcm_token__isnull=False).distinct()
            
            # Collect all FCM tokens
            tokens = []
            
            # Add student tokens
            student_tokens = students.values_list('fcm_token', flat=True)
            tokens.extend(student_tokens)
            
            # Add parent tokens
            parent_tokens = parents.values_list('fcm_token', flat=True)
            tokens.extend(parent_tokens)
            
            # Remove any empty or null tokens
            tokens = [token for token in tokens if token]
            
            # Send push notifications if we have any tokens
            if tokens:
                try:
                    # Send notification to all tokens at once
                    success_count, failure_count, failed_tokens = send_push_notification(
                        "New Meeting Scheduled",
                        f"A new meeting has been scheduled for {meeting_date} at {meeting_time}",
                        tokens
                    )
                    
                    if failure_count > 0:
                        print(f"Failed to send notifications to {failure_count} devices")
                        print(f"Failed tokens: {failed_tokens}")
                except Exception as e:
                    print(f"Error sending notifications: {str(e)}")
            
            return JsonResponse({"success": True, "message": "Meeting scheduled successfully."})
        
        return JsonResponse({"success": False, "message": "Invalid request method."})
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def get_meeting(request, meeting_id):
    """Get meeting details"""
    try:
        # Check if user is HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can view meeting details."})
        
        # Get meeting
        meeting = get_object_or_404(TeacherParentMeeting, id=meeting_id)
        
        # Prepare response data
        response_data = {
            "success": True,
            "meeting": {
                "id": meeting.id,
                "meeting_date": meeting.meeting_date.strftime("%Y-%m-%d"),
                "meeting_time": meeting.meeting_time.strftime("%H:%M"),
                "duration": meeting.duration,
                "status": meeting.status,
                "status_display": meeting.get_status_display(),
                "agenda": meeting.agenda,
                "notes": meeting.notes,
                "is_online": meeting.is_online,
                "meeting_link": meeting.meeting_link,
                "cancellation_reason": meeting.cancellation_reason,
                "created_at": meeting.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        return JsonResponse(response_data)
        
    except TeacherParentMeeting.DoesNotExist:
        return JsonResponse({"success": False, "message": "Meeting not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def edit_meeting(request, meeting_id):
    """Edit an existing meeting"""
    try:
        # Check if user is HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can edit meetings."})
        
        # Get meeting
        meeting = get_object_or_404(TeacherParentMeeting, id=meeting_id)
        
        if request.method == "PUT":
            meeting_date = request.POST.get("meeting_date")
            meeting_time = request.POST.get("meeting_time")
            duration = request.POST.get("duration")
            agenda = request.POST.get("agenda")
            notes = request.POST.get("notes", "")  # Get notes field with empty string default
            is_online = request.POST.get("is_online") == "true"
            meeting_link = request.POST.get("meeting_link", "")  # Default to empty string
            
            # Validate required fields
            if not all([meeting_date, meeting_time, duration]):
                return JsonResponse({"error": "Date, time and duration are required"}, status=400)
            
            # Update meeting
            meeting.meeting_date = meeting_date
            meeting.meeting_time = meeting_time
            meeting.duration = duration
            meeting.agenda = agenda
            meeting.notes = notes  # Save notes field
            meeting.is_online = is_online
            meeting.meeting_link = meeting_link  # Always set meeting_link, even if empty
            meeting.status = "rescheduled" if meeting.status == "scheduled" else meeting.status
            
            meeting.save()
            
            # Get students and parents to notify
            students = Student.objects.filter(course=request.user.course, fcm_token__isnull=False)
            student_ids = students.values_list('id', flat=True)
            parents = Parent.objects.filter(students__in=student_ids, fcm_token__isnull=False).distinct()
            
            # Collect FCM tokens
            tokens = list(students.values_list('fcm_token', flat=True)) + list(parents.values_list('fcm_token', flat=True))
            tokens = [token for token in tokens if token]
            
            # Send notifications
            if tokens:
                try:
                    success_count, failure_count, failed_tokens = send_push_notification(
                        "Meeting Updated",
                        f"Meeting scheduled for {meeting_date} at {meeting_time} has been updated",
                        tokens
                    )
                    
                    if failure_count > 0:
                        print(f"Failed to send notifications to {failure_count} devices")
                except Exception as e:
                    print(f"Error sending notifications: {str(e)}")
            
            return JsonResponse({"success": True, "message": "Meeting updated successfully."})
        
        return JsonResponse({"success": False, "message": "Invalid request method."})
        
    except TeacherParentMeeting.DoesNotExist:
        return JsonResponse({"success": False, "message": "Meeting not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def cancel_meeting(request, meeting_id):
    """Cancel a meeting"""
    try:
        # Check if user is HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can cancel meetings."})
        
        # Get meeting
        meeting = get_object_or_404(TeacherParentMeeting, id=meeting_id)
        
        if request.method == "POST":
            cancellation_reason = request.POST.get("cancellation_reason")
            
            if not cancellation_reason:
                return JsonResponse({"success": False, "message": "Cancellation reason is required."})
            
            # Update meeting
            meeting.status = "cancelled"
            meeting.cancellation_reason = cancellation_reason
            meeting.save()
            
            # Get students and parents to notify
            students = Student.objects.filter(course=request.user.course, fcm_token__isnull=False)
            student_ids = students.values_list('id', flat=True)
            parents = Parent.objects.filter(students__in=student_ids, fcm_token__isnull=False).distinct()
            
            # Collect FCM tokens
            tokens = list(students.values_list('fcm_token', flat=True)) + list(parents.values_list('fcm_token', flat=True))
            tokens = [token for token in tokens if token]
            
            # Send notifications
            if tokens:
                try:
                    success_count, failure_count, failed_tokens = send_push_notification(
                        "Meeting Cancelled",
                        f"Meeting scheduled for {meeting.meeting_date} at {meeting.meeting_time} has been cancelled",
                        tokens
                    )
                    
                    if failure_count > 0:
                        print(f"Failed to send notifications to {failure_count} devices")
                except Exception as e:
                    print(f"Error sending notifications: {str(e)}")
            
            return JsonResponse({"success": True, "message": "Meeting cancelled successfully."})
        
        return JsonResponse({"success": False, "message": "Invalid request method."})
        
    except TeacherParentMeeting.DoesNotExist:
        return JsonResponse({"success": False, "message": "Meeting not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def get_meeting_notes(request, meeting_id):
    """Get meeting notes"""
    try:
        # Check if user is HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can view meeting notes."})
        
        # Get meeting
        meeting = get_object_or_404(TeacherParentMeeting, id=meeting_id)
        
        return JsonResponse({
            "success": True,
            "notes": meeting.notes or "No notes available"
        })
        
    except TeacherParentMeeting.DoesNotExist:
        return JsonResponse({"success": False, "message": "Meeting not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def get_meeting_agenda(request, meeting_id):
    """Get meeting agenda"""
    try:
        # Check if user is HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can view meeting agenda."})
        
        # Get meeting
        meeting = get_object_or_404(TeacherParentMeeting, id=meeting_id)
        
        return JsonResponse({
            "success": True,
            "agenda": meeting.agenda or "No agenda available"
        })
        
    except TeacherParentMeeting.DoesNotExist:
        return JsonResponse({"success": False, "message": "Meeting not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def get_cancellation_reason(request, meeting_id):
    """Get meeting cancellation reason"""
    try:
        # Check if user is HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can view cancellation reasons."})
        
        # Get meeting
        meeting = get_object_or_404(TeacherParentMeeting, id=meeting_id)
        
        if meeting.status != "cancelled":
            return JsonResponse({"success": False, "message": "Meeting is not cancelled."})
        
        return JsonResponse({
            "success": True,
            "reason": meeting.cancellation_reason or "No reason provided"
        })
        
    except TeacherParentMeeting.DoesNotExist:
        return JsonResponse({"success": False, "message": "Meeting not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

# API endpoints for meeting management
@login_required
@require_http_methods(["GET"])
def api_get_meeting(request, meeting_id):
    """API endpoint to get meeting details"""
    try:
        # Get meeting
        meeting = get_object_or_404(TeacherParentMeeting, id=meeting_id)
        
        # Prepare response data
        response_data = {
            "id": meeting.id,
            "meeting_date": meeting.meeting_date.strftime("%Y-%m-%d"),
            "meeting_time": meeting.meeting_time.strftime("%H:%M"),
            "duration": meeting.duration,
            "status": meeting.status,
            "status_display": meeting.get_status_display(),
            "agenda": meeting.agenda,
            "notes": meeting.notes,
            "is_online": meeting.is_online,
            "meeting_link": meeting.meeting_link,
            "cancellation_reason": meeting.cancellation_reason,
            "created_at": meeting.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return JsonResponse(response_data)
        
    except TeacherParentMeeting.DoesNotExist:
        return JsonResponse({"error": "Meeting not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_create_meeting(request):
    """API endpoint to create a new meeting"""
    try:
        # Check if user is HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"error": "Only HODs can schedule meetings"}, status=403)
        
        # Get form data
        meeting_date = request.POST.get("meeting_date")
        meeting_time = request.POST.get("meeting_time")
        duration = request.POST.get("duration")
        agenda = request.POST.get("agenda", "")
        is_online = request.POST.get("is_online") == "true"
        meeting_link = request.POST.get("meeting_link", "") or ""  # Ensure never NULL
        
        # Validate required fields
        if not all([meeting_date, meeting_time, duration]):
            return JsonResponse({"error": "Date, time and duration are required"}, status=400)
        
        # Create meeting
        meeting = TeacherParentMeeting(
            meeting_date=meeting_date,
            meeting_time=meeting_time,
            duration=duration,
            agenda=agenda,
            is_online=is_online,
            meeting_link=meeting_link,  # Now guaranteed to be at least empty string
            status="scheduled"
        )
        
        meeting.save()
        
        # Return success response
        return JsonResponse({
            "id": meeting.id,
            "message": "Meeting scheduled successfully" 
        })
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["PUT", "POST"])
def api_update_meeting(request, meeting_id):
    """API endpoint to update an existing meeting"""
    try:
        # Check if user is HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"error": "Only HODs can edit meetings"}, status=403)
        
        # Get meeting
        meeting = get_object_or_404(TeacherParentMeeting, id=meeting_id)
        
        # Get form data
        meeting_date = request.POST.get("meeting_date")
        meeting_time = request.POST.get("meeting_time")
        duration = request.POST.get("duration")
        agenda = request.POST.get("agenda")
        notes = request.POST.get("notes", "")  # Get notes field with empty string default
        is_online = request.POST.get("is_online") == "true"
        meeting_link = request.POST.get("meeting_link", "")  # Default to empty string
        
        # Validate required fields
        if not all([meeting_date, meeting_time, duration]):
            return JsonResponse({"error": "Date, time and duration are required"}, status=400)
        
        # Update meeting
        meeting.meeting_date = meeting_date
        meeting.meeting_time = meeting_time
        meeting.duration = duration
        meeting.agenda = agenda
        meeting.notes = notes  # Save notes field
        meeting.is_online = is_online
        meeting.meeting_link = meeting_link  # Always set meeting_link, even if empty
        meeting.status = "rescheduled" if meeting.status == "scheduled" else meeting.status
        
        meeting.save()
        
        # Return success response
        return JsonResponse({
            "id": meeting.id,
            "message": "Meeting updated successfully"
        })
        
    except TeacherParentMeeting.DoesNotExist:
        return JsonResponse({"error": "Meeting not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_cancel_meeting(request, meeting_id):
    """API endpoint to cancel a meeting"""
    try:
        # Check if user is HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"error": "Only HODs can cancel meetings"}, status=403)
        
        # Get meeting
        meeting = get_object_or_404(TeacherParentMeeting, id=meeting_id)
        
        # Get cancellation reason
        cancellation_reason = request.POST.get("cancellation_reason")
        
        if not cancellation_reason:
            return JsonResponse({"error": "Cancellation reason is required"}, status=400)
        
        # Update meeting
        meeting.status = "cancelled"
        meeting.cancellation_reason = cancellation_reason
        meeting.save()
        
        # Return success response
        return JsonResponse({
            "id": meeting.id,
            "message": "Meeting cancelled successfully"
        })
        
    except TeacherParentMeeting.DoesNotExist:
        return JsonResponse({"error": "Meeting not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_create_routine(request):
    """API endpoint to create a new routine"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can create routines."})

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})

        course = hod.course

        # Get form data
        subject_id = request.POST.get("subject_id")
        teacher_id = request.POST.get("teacher_id")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        period_or_year = request.POST.get("period_or_year")

        # Validate required fields
        if not subject_id or not teacher_id or not start_time or not end_time or not period_or_year:
            return JsonResponse({"success": False, "message": "All fields are required."})

        # Get subject and teacher objects
        try:
            subject = Subject.objects.get(id=subject_id, course=course)
            teacher = Staff.objects.get(id=teacher_id)
        except (Subject.DoesNotExist, Staff.DoesNotExist):
            return JsonResponse({"success": False, "message": "Invalid subject or teacher."})

        # Create the routine
        routine = Routine(
            course=course,
            subject=subject,
            teacher=teacher,
            start_time=start_time,
            end_time=end_time,
            period_or_year=period_or_year,
            is_active=True
        )
        routine.save()

        return JsonResponse({
            "success": True, 
            "message": "Routine created successfully.",
            "routine_id": routine.id
        })
    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
@require_http_methods(["GET"])
def api_get_routine(request, routine_id):
    """API endpoint to get routine details"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can view routine details."})

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})

        # Get routine and ensure it belongs to the HOD's course
        routine = get_object_or_404(Routine, id=routine_id, course=hod.course)

        # Format time fields properly to ensure they can be used in the form's time inputs
        start_time = routine.start_time.strftime("%H:%M") if routine.start_time else ""
        end_time = routine.end_time.strftime("%H:%M") if routine.end_time else ""

        # Prepare response data with detailed information
        response_data = {
            "success": True,
            "routine": {
                "id": routine.id,
                "subject_id": routine.subject.id,
                "subject_name": routine.subject.name,
                "teacher_id": routine.teacher.id,
                "teacher_name": routine.teacher.name,
                "start_time": start_time,
                "end_time": end_time,
                "period_or_year": routine.period_or_year,
                "is_active": routine.is_active
            }
        }

        # Log the response for debugging
        print(f"API response for routine {routine_id}: {response_data}")
        return JsonResponse(response_data)
    except Exception as e:
        error_message = f"An error occurred while fetching routine {routine_id}: {str(e)}"
        print(error_message)
        return JsonResponse({"success": False, "message": error_message})

@login_required
@csrf_exempt
@require_http_methods(["PUT", "POST"])
def api_update_routine(request, routine_id):
    """API endpoint to update a routine"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can update routines."})

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})

        # Get routine and ensure it belongs to the HOD's course
        routine = get_object_or_404(Routine, id=routine_id, course=hod.course)

        # Handle both PUT and POST methods
        if request.method == 'PUT':
            # For PUT requests, get data from request.POST or parse request.body
            import json
            try:
                if request.body:
                    data = json.loads(request.body)
                else:
                    data = request.POST.dict()
                
                # Extract values from the data dictionary
                subject_id = data.get("subject_id")
                teacher_id = data.get("teacher_id")
                start_time = data.get("start_time")
                end_time = data.get("end_time")
                period_or_year = data.get("period_or_year")
                
                print(f"Received data: {data}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                # Fallback to form data
                subject_id = request.POST.get("subject_id")
                teacher_id = request.POST.get("teacher_id")
                start_time = request.POST.get("start_time")
                end_time = request.POST.get("end_time")
                period_or_year = request.POST.get("period_or_year")
        else:
            # For POST requests, use request.POST directly
            subject_id = request.POST.get("subject_id")
            teacher_id = request.POST.get("teacher_id")
            start_time = request.POST.get("start_time")
            end_time = request.POST.get("end_time")
            period_or_year = request.POST.get("period_or_year")
        
        # Log received data
        print(f"Processing routine update: subject_id={subject_id}, teacher_id={teacher_id}, start_time={start_time}, end_time={end_time}")

        # Validate required fields
        if not subject_id or not teacher_id or not start_time or not end_time:
            error_msg = "All fields are required."
            print(f"Validation error: {error_msg}")
            return JsonResponse({"success": False, "message": error_msg})

        # Get subject and teacher objects
        try:
            subject = Subject.objects.get(id=subject_id, course=hod.course)
            teacher = Staff.objects.get(id=teacher_id)
        except (Subject.DoesNotExist, Staff.DoesNotExist) as e:
            error_msg = "Invalid subject or teacher."
            print(f"Database lookup error: {e}")
            return JsonResponse({"success": False, "message": error_msg})

        # Update routine
        routine.subject = subject
        routine.teacher = teacher
        routine.start_time = start_time
        routine.end_time = end_time
        if period_or_year:
            routine.period_or_year = period_or_year
        routine.save()
        
        print(f"Routine {routine_id} updated successfully")
        return JsonResponse({"success": True, "message": "Routine updated successfully."})
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(f"Error in api_update_routine: {error_msg}")
        return JsonResponse({"success": False, "message": error_msg})

@login_required
@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def api_delete_routine(request, routine_id):
    """API endpoint to delete a routine"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can delete routines."})

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})

        # Get routine and ensure it belongs to the HOD's course
        routine = get_object_or_404(Routine, id=routine_id, course=hod.course)
        
        # Delete the routine
        routine.delete()

        return JsonResponse({"success": True, "message": "Routine deleted successfully."})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def get_student_progress(request):
    """API endpoint to get all student progress data with filtering options"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can access progress data."})

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})

        course = hod.course
        
        # Get batch filter if provided
        batch_id = request.GET.get('batch_id')
        
        # Base query for student progress
        progress_query = CourseTracking.objects.filter(
            student__course=course
        ).select_related("student")
        
        # Apply batch filter if provided
        if batch_id:
            try:
                batch = Batch.objects.get(id=batch_id)
                progress_query = progress_query.filter(student__batches=batch)
            except Batch.DoesNotExist:
                return JsonResponse({"success": False, "message": "Invalid batch selected."})
        
        # Get all progress records ordered by completion percentage
        progress_records = progress_query.order_by("-completion_percentage")
        
        # Calculate metrics
        total_students = progress_records.count()
        avg_completion = progress_records.aggregate(Avg('completion_percentage'))['completion_percentage__avg'] or 0
        avg_completion = round(avg_completion, 1)
        students_on_track = progress_records.filter(completion_percentage__gte=75).count()
        students_at_risk = progress_records.filter(completion_percentage__lt=40).count()
        
        # Prepare progress data
        progress_data = []
        
        for progress in progress_records:
            # Get batch names
            batch_names = ", ".join([batch.name for batch in progress.student.batches.all()])
            
            # Determine status
            if progress.completion_percentage >= 75:
                status = "On Track"
                status_class = "success"
            elif progress.completion_percentage >= 40:
                status = "Needs Attention"
                status_class = "warning"
            else:
                status = "At Risk"
                status_class = "danger"
                
            # Format student data
            student_image = progress.student.image.url if progress.student.image else None
            
            # Add to progress data list
            progress_data.append({
                "student_id": progress.student.id,
                "student_name": progress.student.name,
                "student_image": student_image,
                "batch_names": batch_names,
                "current_period": progress.student.current_period,
                "completion_percentage": progress.completion_percentage,
                "last_updated": progress.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status": status,
                "status_class": status_class
            })
        
        # Prepare response
        response_data = {
            "success": True,
            "total_students": total_students,
            "avg_completion": avg_completion,
            "students_on_track": students_on_track,
            "students_at_risk": students_at_risk,
            "progress_data": progress_data
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def get_progress(request, progress_id):
    """API endpoint to get details of a specific student progress record"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can access progress data."})

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})

        course = hod.course
        
        # Get the progress record
        try:
            progress = CourseTracking.objects.get(id=progress_id, student__course=course)
        except CourseTracking.DoesNotExist:
            return JsonResponse({"success": False, "message": "Progress record not found."})
        
        # Get student data
        student = progress.student
        
        # Format batch names
        batch_names = [batch.name for batch in student.batches.all()]
        
        # Prepare progress data
        progress_data = {
            "id": progress.id,
            "completion_percentage": progress.completion_percentage,
            "progress_status": progress.progress_status,
            "notes": progress.notes or "",
            "last_updated": progress.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # Prepare student data
        student_data = {
            "id": student.id,
            "name": student.name,
            "image": student.image.url if student.image else None,
            "current_period": student.current_period,
            "batches": batch_names,
        }
        
        return JsonResponse({
            "success": True,
            "progress": progress_data,
            "student": student_data
        })
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})

@login_required
def edit_progress(request, progress_id):
    """API endpoint to update a student progress record"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            return JsonResponse({"success": False, "message": "Only HODs can update progress data."})

        # Get the HOD's course
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            return JsonResponse({"success": False, "message": "You are not assigned as HOD of any department."})

        course = hod.course
        
        # Check if this is a POST request
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Invalid request method."})
        
        # Get the progress record
        try:
            progress = CourseTracking.objects.get(id=progress_id, student__course=course)
        except CourseTracking.DoesNotExist:
            return JsonResponse({"success": False, "message": "Progress record not found."})
        
        # Get form data
        current_period = request.POST.get('current_period')
        completion_percentage = request.POST.get('completion_percentage')
        notes = request.POST.get('notes', '')
        
        # Validate form data
        if not current_period or not completion_percentage:
            return JsonResponse({"success": False, "message": "Current period and completion percentage are required."})
        
        try:
            current_period = int(current_period)
            completion_percentage = int(completion_percentage)
            
            # Validate current period
            if current_period < 1:
                return JsonResponse({"success": False, "message": "Current period must be at least 1."})
                
            # Maximum period based on course duration and type
            max_period = progress.course.duration
            if progress.course.duration_type == "Semester":
                max_period *= 2  # Two semesters per year
                
            if current_period > max_period:
                return JsonResponse({"success": False, "message": f"Current period cannot exceed {max_period}."})
            
            # Validate completion percentage
            if completion_percentage < 0 or completion_percentage > 100:
                return JsonResponse({"success": False, "message": "Completion percentage must be between 0 and 100."})
                
        except ValueError:
            return JsonResponse({"success": False, "message": "Invalid numeric values provided."})
        
        # Update student's current period
        student = progress.student
        student.current_period = current_period
        student.save(update_fields=['current_period'])
        
        # Update progress record
        progress.completion_percentage = completion_percentage
        progress.notes = notes
        progress.save(update_fields=['completion_percentage', 'notes'])
        
        return JsonResponse({
            "success": True,
            "message": "Progress updated successfully."
        })
        
    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})
