from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.views.decorators.http import require_http_methods, require_GET
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from .models import (
    Staff,
    Student,
    Routine,
    Attendance,
    AttendanceRecord,
    StudentFeedback,
    Staff_leave,
    Notice,
    Institute,
    StaffInstituteFeedback,
    Subject,
    InstituteFeedback
)
from app.admin import custom_admin_site


@login_required
def teacherDashboard(request):
    """View to display the teacher dashboard with their classes and student information"""
    teacher = Staff.objects.get(phone=request.user.phone)  # Get the Staff object
    today = timezone.now().date()
    current_time = timezone.now().time()
    last_week = today - timedelta(days=7)

    # Get only the active routines assigned to this teacher
    today_routines = Routine.objects.filter(
        teacher=teacher,  # Filter by the current teacher
        is_active=True,  # Only include active routines
    ).order_by("start_time")

    # Process routines to include status and attendance
    processed_routines = []
    for routine in today_routines:
        attendance = routine.attendances.filter(date=today).first()

        # Get total students from the course associated with the subject
        total_students = Student.objects.filter(course=routine.subject.course).count()
        attendance_count = (
            0
            if not attendance
            else AttendanceRecord.objects.filter(
                attendance=attendance, student_attend=True
            ).count()
        )

        # Add routine to processed_routines
        processed_routines.append(
            {
                "id": routine.id,  # Add the routine ID for use in the template
                "name": routine.subject.name,
                "start_time": routine.start_time,
                "end_time": routine.end_time,
                "is_completed": attendance is not None,  # Only mark as completed if attendance exists
                "is_ongoing": routine.start_time <= current_time <= routine.end_time,
                "total_students": total_students,
                "attendance_count": attendance_count,
                "semester_or_year": routine.semester_or_year,
                "course_name": routine.subject.course.name,
                "has_attendance": attendance is not None,  # Flag to check if attendance has been taken
            }
        )

    # Calculate class statistics
    total_classes = today_routines.count()
    completed_classes = len([r for r in processed_routines if r["is_completed"]])
    remaining_classes = total_classes - completed_classes

    # Get student statistics - count unique students from teacher's assigned subjects and semesters
    total_students = Student.objects.filter(status="Active").count()
    
    # Get present and absent students for today
    present_students = AttendanceRecord.objects.filter(
        attendance__date=today,
        student_attend=True,
        attendance__routine__teacher=teacher
    ).values('student').distinct().count()

    # Calculate absent students based on teacher's classes today
    today_class_students = set()
    for routine in today_routines:
        students = Student.objects.filter(
            course=routine.subject.course,
            current_semester=routine.semester_or_year,
            status="Active"
        )
        today_class_students.update(students.values_list('id', flat=True))
    
    absent_students = len(today_class_students) - present_students if today_class_students else 0

    # Get average rating from student feedback
    avg_rating = StudentFeedback.objects.filter(
        teacher=teacher
    ).aggregate(Avg('rating'))['rating__avg'] or 0
    avg_rating_rounded = round(avg_rating)
    remaining_stars = 5 - avg_rating_rounded

    # Get leave statistics
    pending_leaves = Staff_leave.objects.filter(staff=teacher, status=0).count()
    approved_leaves = Staff_leave.objects.filter(staff=teacher, status=1).count()
    rejected_leaves = Staff_leave.objects.filter(staff=teacher, status=2).count()

    # Get recent leaves
    recent_leaves = Staff_leave.objects.filter(staff=teacher).order_by('-created_at')[:5]

    # Get recent feedback
    recent_feedback = StudentFeedback.objects.filter(teacher=teacher).order_by('-created_at')[:5]

    # Get notices
    notices = Notice.objects.all().order_by('-created_at')[:5]

    # Get feedback types for institute feedback
    feedback_types = InstituteFeedback.FEEDBACK_TYPE_CHOICES

    # Get institute feedback
    institute_feedback = StaffInstituteFeedback.objects.filter(staff=teacher).order_by('-created_at')[:5]

    # Get all routines for the teacher (for the schedule)
    all_routines = Routine.objects.filter(
        teacher=teacher,
        is_active=True,
        semester_or_year__in=Student.objects.filter(status="Active")
        .values_list('current_semester', flat=True)
        .distinct()
    ).order_by('start_time')

    # Get all attendance records for quick access
    recent_attendance = (
        Attendance.objects.filter(teacher=teacher, date__gte=last_week)
        .select_related("routine")
        .order_by("-date")
    )

    # Add present/total counts to each attendance record
    for attendance in recent_attendance:
        attendance.present_count = AttendanceRecord.objects.filter(
            attendance=attendance, student_attend=True
        ).count()
        attendance.total_count = AttendanceRecord.objects.filter(
            attendance=attendance
        ).count()

    # Attendance Management Data
    routines = Routine.objects.filter(
        teacher=teacher,
        is_active=True
    ).order_by('start_time')

    context = {
        "teacher": teacher,
        "title": "Teacher Dashboard",
        "today_routines": processed_routines,
        "total_classes": total_classes,
        "completed_classes": completed_classes,
        "remaining_classes": remaining_classes,
        "total_students": total_students,
        "present_students": present_students,
        "absent_students": absent_students,
        "avg_rating": avg_rating,
        "avg_rating_rounded": avg_rating_rounded,
        "remaining_stars": remaining_stars,
        "pending_leaves": pending_leaves,
        "approved_leaves": approved_leaves,
        "rejected_leaves": rejected_leaves,
        "recent_leaves": recent_leaves,
        "recent_feedback": recent_feedback,
        "notices": notices,
        "feedback_types": feedback_types,
        "institute_feedback": institute_feedback,
        "all_routines": all_routines,
        "recent_attendance": recent_attendance,
        # Attendance Management Context
        "routines": routines,
        "today": today,
    }

    return render(request, "teacher_dashboard.html", context)


@login_required
def request_staff_leave(request):
    """View to handle leave requests from staff"""
    if request.method == "POST":
        staff = request.user
        date = request.POST.get("date")
        message = request.POST.get("message")

        try:
            # Convert date string to timezone-aware datetime
            leave_date = timezone.datetime.strptime(date, "%Y-%m-%d")
            leave_date = timezone.make_aware(leave_date)
            today = timezone.now()

            if leave_date.date() < today.date():
                messages.error(request, "Leave date cannot be in the past.")
                return redirect("teacherDashboard")

            # Check if leave already exists for this date
            existing_leave = Staff_leave.objects.filter(
                staff=staff, date=leave_date.date()
            ).first()

            if existing_leave:
                messages.error(
                    request, "You have already requested leave for this date."
                )
                return redirect("teacherDashboard")

            # Create leave request
            leave = Staff_leave.objects.create(
                staff=staff,
                date=leave_date.date(),
                message=message,
                status=0,  # Pending status
            )
            messages.success(request, "Leave request submitted successfully.")
        except Exception as e:
            messages.error(request, f"Error submitting leave request: {str(e)}")

        return redirect("teacherDashboard")

    return redirect("teacherDashboard")


@login_required
def submit_staff_institute_feedback(request):
    """View to handle feedback submission from staff to institute"""
    if request.method == "POST":
        staff = request.user
        feedback_type = request.POST.get("feedback_type")
        rating = request.POST.get("rating")
        feedback_text = request.POST.get("feedback_text")
        is_anonymous = request.POST.get("is_anonymous") == "on"

        try:
            # Convert to float first to handle half-stars
            rating_value = float(rating)
            if rating_value < 0.5 or rating_value > 5:
                messages.error(request, "Rating must be between 0.5 and 5")
                return redirect("teacherDashboard")

            # Check if it's a valid half or full star rating
            if rating_value % 0.5 != 0:
                messages.error(request, "Rating must be a whole or half number")
                return redirect("teacherDashboard")

            # Get the institute (assuming one institute for now)
            institute = Institute.objects.first()

            if not institute:
                # Create a default institute if none exists
                institute = Institute.objects.create(
                    name="Default Institute",
                    phone="123456789",
                    email="default@example.com",
                )

            # Get the staff object
            teacher = Staff.objects.get(phone=staff.phone)

            # Check if feedback already exists for this type
            existing_feedback = StaffInstituteFeedback.objects.filter(
                staff=teacher, institute=institute, feedback_type=feedback_type
            ).first()

            if existing_feedback:
                # Update existing feedback
                existing_feedback.rating = rating_value
                existing_feedback.feedback_text = feedback_text
                existing_feedback.is_anonymous = is_anonymous
                existing_feedback.save()
                messages.success(request, "Institute feedback updated successfully.")
            else:
                # Create new feedback
                feedback = StaffInstituteFeedback.objects.create(
                    staff=teacher,
                    institute=institute,
                    feedback_type=feedback_type,
                    rating=rating_value,
                    feedback_text=feedback_text,
                    is_anonymous=is_anonymous,
                )
                messages.success(request, "Institute feedback submitted successfully.")
        except ValueError:
            messages.error(request, "Invalid rating value")
        except Exception as e:
            messages.error(request, f"Error submitting institute feedback: {str(e)}")

        return redirect("teacherDashboard")

    return redirect("teacherDashboard")


@login_required
def save_attendance(request):
    """View to save attendance data"""
    if request.method == "POST":
        teacher = Staff.objects.get(phone=request.user.phone)
        routine_id = request.POST.get("routine_id")
        date_str = request.POST.get("date")

        # Convert class_status to boolean - "Conducted" is True, others are False
        class_status_str = request.POST.get("class_status", "True")
        class_status = class_status_str == "True"

        teacher_attend = request.POST.get("teacher_attend") == "on"

        try:
            # Validate routine - strict check to ensure teacher can only access their assigned routines
            routine = Routine.objects.get(
                id=routine_id,
                teacher=teacher,  # Ensure this routine is assigned to this teacher
                is_active=True,  # Only allow active routines
            )

            # Validate date
            attendance_date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()

            # Get or create attendance record
            attendance, created = Attendance.objects.get_or_create(
                routine=routine,
                date=attendance_date,
                defaults={
                    "teacher": teacher,
                    "class_status": class_status,
                    "teacher_attend": teacher_attend,
                },
            )

            if not created:
                # Update existing attendance
                attendance.class_status = class_status
                attendance.teacher_attend = teacher_attend
                attendance.save()

            # Process student attendance
            for key, value in request.POST.items():
                if key.startswith("student_"):
                    student_id = key.replace("student_", "")
                    student_attend = value == "on"

                    try:
                        # Convert student_id to integer to ensure proper lookup
                        student_id_int = int(student_id)
                        student = Student.objects.get(id=student_id_int)

                        # Get or create attendance record for this student
                        record, _ = AttendanceRecord.objects.get_or_create(
                            attendance=attendance,
                            student=student,
                            defaults={"student_attend": student_attend},
                        )

                        # Update if record already exists
                        if record.student_attend != student_attend:
                            record.student_attend = student_attend
                            record.save()

                    except Student.DoesNotExist:
                        continue

            messages.success(
                request,
                f"Attendance for {attendance_date.strftime('%d %b, %Y')} saved successfully.",
            )

        except Routine.DoesNotExist:
            messages.error(
                request,
                "You do not have permission to take attendance for this class. Only teachers assigned to this class can manage its attendance.",
            )
        except ValueError:
            messages.error(request, "Invalid date format.")
        except Exception as e:
            messages.error(request, f"Error saving attendance: {str(e)}")

        # Redirect to teacher dashboard after saving attendance
        return redirect("teacherDashboard")

    return redirect("teacherDashboard")


@login_required
@require_GET
def get_subject_schedule(request):
    """View to get schedule for a subject"""
    teacher = Staff.objects.get(phone=request.user.phone)
    subject_id = request.GET.get("subject_id")

    if not subject_id:
        return JsonResponse({"success": False, "message": "Subject ID is required"})

    try:
        routines = Routine.objects.filter(
            teacher=teacher, subject_id=subject_id, is_active=True
        ).values("id", "start_time", "end_time", "semester_or_year")

        return JsonResponse({"success": True, "schedule": list(routines)})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
def teacher_update_profile_picture(request):
    """View to handle profile picture update for teachers"""
    if request.method == "POST":
        teacher = Staff.objects.get(phone=request.user.phone)
        profile_picture = request.FILES.get("profile_picture")

        if profile_picture:
            try:
                # Update the teacher's profile picture
                teacher.image = profile_picture
                teacher.save()
                messages.success(request, "Profile picture updated successfully.")
            except Exception as e:
                messages.error(request, f"Error updating profile picture: {str(e)}")
        else:
            messages.error(request, "No profile picture uploaded.")

        return redirect("teacherDashboard")

    return redirect("teacherDashboard")


@login_required
def teacher_change_password(request):
    """View to handle password change for teachers"""
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Get the current user
        user = request.user

        # Validate inputs
        if not current_password or not new_password or not confirm_password:
            messages.error(request, "All password fields are required.")
            return redirect("teacherDashboard")

        # Check if current password is correct
        if not check_password(current_password, user.password):
            messages.error(request, "Current password is incorrect.")
            return redirect("teacherDashboard")

        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("teacherDashboard")

        # Check if new password is strong enough (add more criteria as needed)
        if len(new_password) < 8:
            messages.error(request, "New password must be at least 8 characters long.")
            return redirect("teacherDashboard")

        try:
            # Update the password
            user.password = make_password(new_password)
            user.save()
            messages.success(
                request,
                "Password changed successfully. Please log in again with your new password.",
            )
            return redirect(
                "login"
            )  # Redirect to login page to log in with new password
        except Exception as e:
            messages.error(request, f"Error changing password: {str(e)}")

        return redirect("teacherDashboard")

    return redirect("teacherDashboard")


@login_required
def get_attendance_form(request):
    """View to handle AJAX request for getting attendance form"""
    routine_id = request.GET.get('routine_id')
    date_str = request.GET.get('date')
    
    if not routine_id or not date_str:
        return JsonResponse({
            'error': 'Missing required parameters'
        })
    
    try:
        routine = Routine.objects.get(id=routine_id, teacher=request.user)
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get existing attendance data if any
        attendance_data = {
            'teacher_attend': False,
            'class_status': True,
            'records': {}
        }
        
        try:
            # Get attendance record with all related data in one query
            attendance = Attendance.objects.select_related('routine').get(
                routine=routine,
                date=date
            )
            
            # Get all attendance records for this attendance in one query
            records = AttendanceRecord.objects.filter(attendance=attendance).select_related('student')
            
            attendance_data = {
                'id': attendance.id,
                'date': attendance.date.strftime('%Y-%m-%d'),
                'teacher_attend': attendance.teacher_attend,
                'class_status': attendance.class_status,
                'records': {
                    str(record.student.id): record.student_attend 
                    for record in records
                }
            }
        except Attendance.DoesNotExist:
            # No existing attendance record found - return default values
            pass
        
        return JsonResponse(attendance_data)
        
    except Routine.DoesNotExist:
        return JsonResponse({
            'error': 'Invalid routine selected'
        }, status=404)
    except ValueError:
        return JsonResponse({
            'error': 'Invalid date format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
def get_students(request):
    """View to handle AJAX request for getting students list"""
    from django.http import JsonResponse
    
    routine_id = request.GET.get('routine_id')
    
    if not routine_id:
        return JsonResponse({'error': 'Missing routine_id parameter'}, status=400)
    
    try:
        routine = Routine.objects.get(id=routine_id, teacher=request.user)
        
        # Get students for this routine
        students = Student.objects.filter(
            course=routine.subject.course,
            current_semester=routine.semester_or_year
        ).order_by('name')
        
        # If no students found, try a more flexible approach
        if not students.exists():
            students = Student.objects.filter(
                course=routine.subject.course
            ).order_by('name')
        
        # Format student data for JSON response
        student_data = [{
            'id': student.id,
            'name': student.name
        } for student in students]
        
        return JsonResponse({
            'students': student_data
        })
        
    except Routine.DoesNotExist:
        return JsonResponse({'error': 'Invalid routine selected'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
