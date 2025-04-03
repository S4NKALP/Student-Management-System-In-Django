from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import (
    Student,
    Course,
    CourseTracking,
    Student_Leave,
    Staff_leave,
    Attendance,
    AttendanceRecord,
    StudentFeedback,
    Routine,
    Staff,
    Notice,
    Institute,
    InstituteFeedback,
    Subject,
    Batch,
)
from app.admin import custom_admin_site
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
from django.db.models.base import transaction
from .utils import generate_otp, generate_secret_key, store_secret_key, verify_otp, send_otp_sms
from django.conf import settings
from dotenv import load_dotenv
from .firebase import save_fcm_token, get_firebase_js, FCMDevice
from django.template.loader import render_to_string
from django.views.static import serve
# Import views from studentviews.py
from .studentviews import (
    studentDashboard,
    request_leave,
    submit_feedback,
    submit_institute_feedback,
    get_subject_files,
)

# Import views from staffviews.py
from .staffviews import (
    teacherDashboard,
    request_staff_leave,
    submit_staff_institute_feedback,
    save_attendance,
    get_subject_schedule,
    teacher_update_profile_picture,
    teacher_change_password,
)

from django.contrib.auth.hashers import check_password

# Load environment variables
load_dotenv()

# Create your views here.



@login_required
def dashboard(request):
    """Main dashboard view that redirects to appropriate dashboard based on user role"""
    user = request.user
    user_groups = user.groups.values_list("name", flat=True)
    

    
    # Redirect based on user role
    if "Student" in user_groups:
        print("Redirecting to student dashboard")
        return redirect("studentDashboard")
    elif "Teacher" in user_groups:
        print("Redirecting to teacher dashboard")
        return redirect("teacherDashboard")
    elif user.is_superuser or user.is_staff:
        # Admin users get the admin dashboard
        print("Showing admin dashboard")
        
        # Get current date and date ranges
        today = timezone.now().date()
        last_week = timezone.now() - timedelta(days=7)
        last_month = timezone.now() - timedelta(days=30)
        
        # Debug prints for user authentication
        print(f"Is authenticated: {request.user.is_authenticated}")
        print(f"Is staff: {request.user.is_staff}")
        print(f"Is superuser: {request.user.is_superuser}")
        print("-------------------------\n")
        
        # Student Statistics - with debug prints
        total_students = Student.objects.count()
        print("\nDEBUG Student Statistics:")
        print("-------------------------")
        print(f"Total students (from count): {total_students}")
        
        # Get all students and print their statuses
        all_students = Student.objects.all()
        print("\nAll students and their statuses:")
        for student in all_students:
            print(f"- {student.name}: {student.status}")
        
        active_students = Student.objects.filter(status="Active").count()
        print(f"\nActive students: {active_students}")
        
        completed_students = Student.objects.filter(status="Completed").count()
        print(f"Completed students: {completed_students}")
        
        on_leave_students = Student.objects.filter(status="Leave").count()
        print(f"Students on leave: {on_leave_students}")
        
        print(f"\nSum of status counts: {active_students + completed_students + on_leave_students}")
        print("-------------------------\n")

        # Staff Statistics
        total_staff = Staff.objects.count()
        active_staff = Staff.objects.filter(is_active=True).count()
        staff_on_leave = (
            Staff_leave.objects.filter(status=1).values("staff").distinct().count()
        )

        # Course Statistics
        total_courses = Course.objects.count()
        active_courses = (
            Course.objects.filter(student_trackings__progress_status="In Progress")
            .distinct()
            .count()
        )
        completed_courses = (
            Course.objects.filter(student_trackings__progress_status="Completed")
            .distinct()
            .count()
        )

        # Course Tracking Statistics
        course_trackings = CourseTracking.objects.all()
        in_progress_trackings = course_trackings.filter(progress_status="In Progress")
        completed_trackings = course_trackings.filter(progress_status="Completed")
        dropped_trackings = course_trackings.filter(progress_status="Dropped")

        # Recent Leave Requests
        recent_student_leaves = Student_Leave.objects.filter(
            created_at__gte=last_week
        ).order_by("-created_at")[:5]

        recent_staff_leaves = Staff_leave.objects.filter(
            created_at__gte=last_week
        ).order_by("-created_at")[:5]

        # Pending Leave Requests
        pending_student_leaves = Student_Leave.objects.filter(status=0)
        pending_staff_leaves = Staff_leave.objects.filter(status=0).order_by("-created_at")

        # Attendance Statistics
        today_classes = Attendance.objects.filter(date=today)
        total_classes = today_classes.count()
        total_students_today = AttendanceRecord.objects.filter(attendance__in=today_classes).count()
        students_present = AttendanceRecord.objects.filter(
            attendance__in=today_classes, student_attend=True
        ).count()

        # Recent Feedback
        recent_feedback = StudentFeedback.objects.order_by("-created_at")[:5]

        # Recent Institute Feedback
        recent_institute_feedback = InstituteFeedback.objects.filter(
            is_public=True
        ).order_by("-created_at")[:10]

        # Get notices
        notices = Notice.objects.all().order_by("-created_at")

        # Get recent activities
        recent_activities = []

        # Add recent leaves
        for leave in recent_student_leaves:
            recent_activities.append(
                {
                    "title": f"Student Leave Request",
                    "description": f"{leave.student.name} requested leave from {leave.start_date} to {leave.end_date}",
                    "timestamp": leave.created_at,
                }
            )

        for leave in recent_staff_leaves:
            recent_activities.append(
                {
                    "title": f"Staff Leave Request",
                    "description": f"{leave.staff.name} requested leave from {leave.start_date} to {leave.end_date}",
                    "timestamp": leave.created_at,
                }
            )

        # Add recent feedback
        for feedback in recent_feedback:
            recent_activities.append(
                {
                    "title": f"New Feedback",
                    "description": f"Feedback received for {feedback.teacher.name if feedback.teacher else 'Institute'}",
                    "timestamp": feedback.created_at,
                }
            )

        # Add recent institute feedback
        for feedback in recent_institute_feedback:
            recent_activities.append(
                {
                    "title": f"Institute Feedback",
                    "description": f"New feedback from {feedback.display_name}",
                    "timestamp": feedback.created_at,
                }
            )

        # Add recent notices
        for notice in notices:
            recent_activities.append(
                {
                    "title": f"New Notice",
                    "description": notice.title,
                    "timestamp": notice.created_at,
                }
            )

        # Sort all activities by timestamp
        recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)
        # Take only the most recent 10 activities
        recent_activities = recent_activities[:10]

        # Teacher Ratings
        teacher_ratings = []
        teachers = Staff.objects.filter(
            Q(designation__icontains="Teacher")
            | Q(designation__icontains="Staff")
            | Q(designation__icontains="Principal")
            | Q(designation__isnull=True)
            | Q(designation="")
        )

        for teacher in teachers:
            feedback = StudentFeedback.objects.filter(teacher=teacher)
            avg_rating = feedback.aggregate(Avg("rating"))["rating__avg"] or 0
            total_reviews = feedback.count()

            # Get total students taught by this teacher
            total_students = (
                AttendanceRecord.objects.filter(attendance__routine__teacher=teacher)
                .values("student")
                .distinct()
                .count()
            )

            teacher_ratings.append(
                {
                    "name": teacher.name,
                    "designation": teacher.designation or "Teacher",
                    "image": teacher.image,
                    "avg_rating": avg_rating,
                    "total_reviews": total_reviews,
                    "total_students": total_students,
                }
            )

        # Sort teachers by average rating (highest first)
        teacher_ratings.sort(key=lambda x: x["avg_rating"], reverse=True)

        # Course Progress Overview
        course_progress = []
        for course in Course.objects.all():
            trackings = course.student_trackings.all()
            if trackings.exists():
                avg_progress = trackings.aggregate(
                    avg_progress=Avg("completion_percentage")
                )["avg_progress"]
                course_progress.append(
                    {
                        "course": course,
                        "total_students": trackings.count(),
                        "in_progress": trackings.filter(
                            progress_status="In Progress"
                        ).count(),
                        "completed": trackings.filter(progress_status="Completed").count(),
                        "average_progress": round(avg_progress, 1) if avg_progress else 0,
                    }
                )

        # Monthly Statistics
        monthly_stats = {
            "new_students": Student.objects.filter(joining_date__gte=last_month).count(),
            "new_staff": Staff.objects.filter(joining_date__gte=last_month).count(),
            "attendance_rate": round(
                (
                    AttendanceRecord.objects.filter(
                        attendance__date__gte=last_month.date(), student_attend=True
                    ).count()
                    / AttendanceRecord.objects.filter(
                        attendance__date__gte=last_month.date()
                    ).count()
                    * 100
                )
                if AttendanceRecord.objects.filter(
                    attendance__date__gte=last_month.date()
                ).exists()
                else 0
            ),
            "leave_requests": Student_Leave.objects.filter(
                created_at__gte=last_month
            ).count()
            + Staff_leave.objects.filter(created_at__gte=last_month).count(),
        }

        context = {
            **custom_admin_site.each_context(
                request
            ),  # This adds the admin context, including the sidebar.
            # Student Statistics
            "total_students": total_students,
            "active_students": active_students,
            "completed_students": completed_students,
            "on_leave_students": on_leave_students,
            # Staff Statistics
            "total_staff": total_staff,
            "active_staff": active_staff,
            "staff_on_leave": staff_on_leave,
            # Course Statistics
            "total_courses": total_courses,
            "active_courses": active_courses,
            "completed_courses": completed_courses,
            # Course Tracking Statistics
            "in_progress_trackings": in_progress_trackings.count(),
            "completed_trackings": completed_trackings.count(),
            "dropped_trackings": dropped_trackings.count(),
            # Leave Requests
            "recent_student_leaves": recent_student_leaves,
            "recent_staff_leaves": recent_staff_leaves,
            "pending_student_leaves": pending_student_leaves,
            "pending_staff_leaves": pending_staff_leaves,
            # Attendance Statistics
            "total_classes_today": total_classes,
            "total_students_today": total_students_today,
            "students_present": students_present,
            "attendance_rate": round(
                (students_present / total_students_today * 100) if total_students_today > 0 else 0
            ),
            # Feedback
            "recent_feedback": recent_feedback,
            "recent_institute_feedback": recent_institute_feedback,
            "teacher_ratings": teacher_ratings,
            # Course Progress
            "course_progress": course_progress,
            # Monthly Statistics
            "monthly_stats": monthly_stats,
            "notices": notices,  # Add notices to context
            "recent_activities": recent_activities,  # Add recent activities to context
        }

        return render(request, "dashboard.html", context)
    else:
        # If user doesn't belong to any specific group, try to determine user type
        print("User doesn't belong to any specific group")
        if hasattr(user, 'student'):
            print("User has student attribute, redirecting to student dashboard")
            return redirect("studentDashboard")
        elif hasattr(user, 'staff'):
            print("User has staff attribute, redirecting to teacher dashboard")
            return redirect("teacherDashboard")
        else:
            print("Unknown user type, showing default dashboard")
            return render(request, "dashboard.html", {"unknown_user_type": True})


@login_required
def update_profile(request):
    if request.method == "POST":
        user = request.user
        user_groups = user.groups.values_list("name", flat=True)

        # Handle profile image update
        if "profile_image" in request.FILES:
            try:
                image = request.FILES["profile_image"]
                
                if "Student" in user_groups:
                    student = Student.objects.get(id=user.id)
                    if student.image:
                        # Delete old image if updating
                        if os.path.isfile(student.image.path):
                            os.remove(student.image.path)
                    # Save new image
                    student.image = image
                    student.save()
                    messages.success(request, "Profile picture updated successfully.")
                
                elif "Teacher" in user_groups:
                    staff = Staff.objects.get(id=user.id)
                    if staff.image:
                        # Delete old image if updating
                        if os.path.isfile(staff.image.path):
                            os.remove(staff.image.path)
                    # Save new image
                    staff.image = image
                    staff.save()
                    messages.success(request, "Profile picture updated successfully.")
                
                else:
                    messages.error(request, "User profile not found. Please make sure you are logged in as a student or staff member.")
            
            except (Student.DoesNotExist, Staff.DoesNotExist) as e:
                messages.error(request, "User profile not found in the database.")
            except Exception as e:
                messages.error(request, f"Error updating profile picture: {str(e)}")
        else:
            messages.error(request, "No profile picture uploaded.")

        # Redirect based on user type
        if "Student" in user_groups:
            return redirect("studentDashboard")
        elif "Teacher" in user_groups:
            return redirect("teacherDashboard")
        else:
            return redirect("dashboard")

    return redirect("dashboard")


@login_required
def change_password(request):
    if request.method == "POST":
        user = request.user
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # Validate input
        if not all([current_password, new_password, confirm_password]):
            if is_ajax:
                return JsonResponse({"success": False, "error": "All password fields are required."})
            messages.error(request, "All password fields are required.")
            return redirect("studentDashboard")

        if new_password != confirm_password:
            if is_ajax:
                return JsonResponse({"success": False, "error": "New passwords do not match."})
            messages.error(request, "New passwords do not match.")
            return redirect("studentDashboard")

        # Check current password
        if not user.check_password(current_password):
            if is_ajax:
                return JsonResponse({"success": False, "error": "Current password is incorrect."})
            messages.error(request, "Current password is incorrect.")
            return redirect("studentDashboard")

        # Set new password
        try:
            user.set_password(new_password)
            user.save()
            if is_ajax:
                return JsonResponse({"success": True})
            
            messages.success(
                request, "Password changed successfully. Please login again."
            )
            return redirect("login")
        except Exception as e:
            if is_ajax:
                return JsonResponse({"success": False, "error": f"Error changing password: {str(e)}"})
            messages.error(request, f"Error changing password: {str(e)}")

        # Redirect based on user type
        if hasattr(user, "student"):
            return redirect("studentDashboard")
        elif hasattr(user, "staff"):
            return redirect("teacherDashboard")
        else:
            return redirect("dashboard")

    return redirect("dashboard")


@login_required
@require_GET
def get_subjects(request):
    """Get subjects for a course and semester"""
    course_id = request.GET.get("course_id")
    semester = request.GET.get("semester", 1)

    if not course_id:
        return JsonResponse({"success": False, "message": "Course ID is required"})

    try:
        subjects = Subject.objects.filter(
            course_id=course_id, semester_or_year=semester
        ).values("id", "name")

        return JsonResponse({"success": True, "subjects": list(subjects)})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
@require_GET
def get_teachers(request):
    """Get teachers for the institute"""
    try:
        teachers = Staff.objects.filter(
            Q(designation__icontains="Teacher")
            | Q(designation__icontains="Staff")
            | Q(designation__icontains="Principal")
            | Q(designation__isnull=True)
            | Q(designation="")
        ).values("id", "name")

        return JsonResponse({"success": True, "teachers": list(teachers)})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
@require_GET
def get_course_duration(request):
    """Get course duration details"""
    course_id = request.GET.get("course_id")

    if not course_id:
        return JsonResponse({"success": False, "message": "Course ID is required"})

    try:
        course = Course.objects.get(id=course_id)

        # Calculate number of semesters or years
        total_periods = course.duration
        if course.duration_type == "Semester":
            total_periods = course.duration * 2  # 2 semesters per year

        # Create a list of periods
        periods = []
        for i in range(1, total_periods + 1):
            if course.duration_type == "Semester":
                periods.append({"value": i, "label": f"Semester {i}"})
            else:
                periods.append({"value": i, "label": f"Year {i}"})

        return JsonResponse(
            {
                "success": True,
                "course": {
                    "id": course.id,
                    "name": course.name,
                    "duration": course.duration,
                    "duration_type": course.duration_type,
                    "total_periods": total_periods,
                    "periods": periods,
                },
            }
        )
    except Course.DoesNotExist:
        return JsonResponse({"success": False, "message": "Course not found"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
def approve_student_leave(request, leave_id):
    """View to approve a student leave request"""
    if request.method == "POST":
        leave = get_object_or_404(Student_Leave, id=leave_id)
        leave.status = 1  # Approved
        leave.save()
        messages.success(
            request, f"Leave request for {leave.student.name} has been approved."
        )
    return redirect("dashboard")


@login_required
def reject_student_leave(request, leave_id):
    """View to reject a student leave request"""
    if request.method == "POST":
        leave = get_object_or_404(Student_Leave, id=leave_id)
        leave.status = 2  # Rejected
        leave.save()
        messages.warning(
            request, f"Leave request for {leave.student.name} has been rejected."
        )
    return redirect("dashboard")


@login_required
def approve_staff_leave(request, leave_id):
    """View to approve a staff leave request"""
    if request.method == "POST":
        leave = get_object_or_404(Staff_leave, id=leave_id)
        leave.status = 1  # Approved
        leave.save()
        messages.success(
            request, f"Leave request for {leave.staff.name} has been approved."
        )
    return redirect("dashboard")


@login_required
def reject_staff_leave(request, leave_id):
    """View to reject a staff leave request"""
    if request.method == "POST":
        leave = get_object_or_404(Staff_leave, id=leave_id)
        leave.status = 2  # Rejected
        leave.save()
        messages.warning(
            request, f"Leave request for {leave.staff.name} has been rejected."
        )
    return redirect("dashboard")


@login_required
def add_notice(request):
    if request.method == "POST":
        title = request.POST.get("title")
        message = request.POST.get("message")
        image = request.FILES.get("image")

        if title and message:
            notice = Notice.objects.create(title=title, message=message, image=image)
            messages.success(request, "Notice added successfully.")
        else:
            messages.error(request, "Title and message are required.")

    return redirect("dashboard")


@login_required
def delete_notice(request, notice_id):
    if request.method == "POST":
        try:
            notice = Notice.objects.get(id=notice_id)
            notice.delete()
            return JsonResponse({"success": True})
        except Notice.DoesNotExist:
            return JsonResponse({"success": False, "error": "Notice not found"})

    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def student_dashboard(request):
    student = request.user.student
    today = timezone.now().date()
    
    # Get attendance summary
    attendance_records = AttendanceRecord.objects.filter(student=student)
    total_classes = attendance_records.count()
    attended_classes = attendance_records.filter(student_attend=True).count()
    attendance_percentage = (attended_classes / total_classes * 100) if total_classes > 0 else 0
    
    # Calculate current streak
    current_streak = 0
    longest_streak = 0
    temp_streak = 1
    
    for record in attendance_records.order_by('-attendance__date'):
        if record.student_attend:
            current_streak += 1
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            break
    
    attendance_summary = {
        'total_classes': total_classes,
        'attendance_percentage': attendance_percentage,
        'current_streak': current_streak,
        'longest_streak': longest_streak
    }
    
    # Get course tracking summary
    course_trackings = CourseTracking.objects.filter(student=student)
    course_summary = {
        'total_courses': course_trackings.count(),
        'completed_courses': course_trackings.filter(progress_status='Completed').count(),
        'ongoing_courses': course_trackings.filter(progress_status='In Progress').count(),
        'completion_percentage': (
            sum(tracking.completion_percentage for tracking in course_trackings) / course_trackings.count()
            if course_trackings.exists() else 0
        )
    }
    
    # Get recent leaves
    recent_leaves = Student_Leave.objects.filter(student=student).order_by('-created_at')[:5]
    
    # Get recent feedback
    recent_feedback = StudentFeedback.objects.filter(student=student).order_by('-created_at')[:5]
    
    # Get notices
    notices = Notice.objects.all().order_by('-created_at')[:5]
    
    # Get attendance records
    attendance_records = AttendanceRecord.objects.filter(student=student).order_by('-attendance__date')[:5]
    
    # Get leave counts
    pending_leaves = Student_Leave.objects.filter(student=student, status=0).count()
    approved_leaves = Student_Leave.objects.filter(student=student, status=1).count()
    rejected_leaves = Student_Leave.objects.filter(student=student, status=2).count()
    
    # Get course details from course tracking
    course_details = []
    for tracking in course_trackings:
        course_info = {
            'name': tracking.course.name,
            'start_date': tracking.start_date,
            'duration': tracking.course.duration,
            'duration_type': tracking.course.duration_type,
            'current_semester': tracking.current_semester,
            'progress_status': tracking.progress_status,
            'completion_percentage': tracking.completion_percentage,
            'semester_start_date': tracking.semester_start_date,
            'semester_end_date': tracking.semester_end_date,
            'expected_end_date': tracking.expected_end_date,
            'actual_end_date': tracking.actual_end_date,
            'remaining_days': tracking.remaining_days,
            'total_remaining_days': tracking.total_remaining_days
        }
        course_details.append(course_info)
    
    context = {
        'student': student,
        'attendance_summary': attendance_summary,
        'course_summary': course_summary,
        'recent_leaves': recent_leaves,
        'recent_feedback': recent_feedback,
        'notices': notices,
        'attendance_records': attendance_records,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'rejected_leaves': rejected_leaves,
        'course_details': course_details,
    }
    return render(request, 'student_dashboard.html', context)

@login_required
def teacher_dashboard(request):
    teacher = request.user.teacher
    today = timezone.now().date()
    
    # Get today's routines
    today_routines = Routine.objects.filter(
        teacher=teacher,
        day_of_week=today.weekday()
    ).order_by('start_time')
    
    # Get attendance summary
    attendance_records = Attendance.objects.filter(routine__teacher=teacher)
    total_classes = attendance_records.count()
    total_students = AttendanceRecord.objects.filter(attendance__routine__teacher=teacher).count()
    present_students = AttendanceRecord.objects.filter(
        attendance__routine__teacher=teacher,
        student_attend=True
    ).count()
    
    attendance_summary = {
        'total_classes': total_classes,
        'total_students': total_students,
        'present_students': present_students,
        'attendance_percentage': (present_students / total_students * 100) if total_students > 0 else 0
    }
    
    # Get recent leaves
    recent_leaves = Student_Leave.objects.filter(
        Q(status=0) | Q(status=1)
    ).order_by('-created_at')[:5]
    
    # Get recent feedback
    recent_feedback = StudentFeedback.objects.filter(teacher=teacher).order_by('-created_at')[:5]
    
    # Get notices
    notices = Notice.objects.all().order_by('-created_at')[:5]
    
    # Get attendance records
    attendance_records = Attendance.objects.filter(routine__teacher=teacher).order_by('-date')[:5]
    
    # Get leave counts
    pending_leaves = Student_Leave.objects.filter(status=0).count()
    approved_leaves = Student_Leave.objects.filter(status=1).count()
    rejected_leaves = Student_Leave.objects.filter(status=2).count()
    
    context = {
        'teacher': teacher,
        'today_routines': today_routines,
        'attendance_summary': attendance_summary,
        'recent_leaves': recent_leaves,
        'recent_feedback': recent_feedback,
        'notices': notices,
        'attendance_records': attendance_records,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'rejected_leaves': rejected_leaves,
    }
    return render(request, 'teacher_dashboard.html', context)

@login_required
@require_POST
def save_fcm_token(request):
    try:
        data = json.loads(request.body)
        token = data.get('token')
        
        if not token:
            return JsonResponse({'error': 'Token is required'}, status=400)
            
        user = request.user
        user_groups = user.groups.values_list("name", flat=True)
        
        # Save token to the appropriate user model
        if "Student" in user_groups:
            user.fcm_token = token
            user.save()
        elif "Teacher" in user_groups:
            user.fcm_token = token
            user.save()
            
        # Update or create FCMDevice
        device, created = FCMDevice.objects.update_or_create(
            token=token,
            defaults={'is_active': True}
        )
            
        return JsonResponse({
            'status': 'success',
            'device_id': device.id,
            'created': created
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        
def serve_firebase_sw(request):
    """Serve Firebase service worker with correct MIME type"""
    
    # Get the path to the service worker in the static directory
    sw_path = os.path.join(settings.STATICFILES_DIRS[0], 'firebase-messaging-sw.js')
    
    # If the file doesn't exist in static directory, try staticfiles
    if not os.path.exists(sw_path):
        sw_path = os.path.join(settings.STATIC_ROOT, 'firebase-messaging-sw.js')
    
    response = serve(request, 'firebase-messaging-sw.js', os.path.dirname(sw_path))
    response['Content-Type'] = 'application/javascript'
    return response

@login_required
def check_weak_password(request):
    """Check if the current user's password is '123'"""
    user = request.user
    is_weak = check_password('123', user.password)
    return JsonResponse({'is_weak': is_weak})
