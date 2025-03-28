from app.models import FCMDevice
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
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
from django.views.decorators.http import require_http_methods, require_GET
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
from django.db.models.base import transaction
from .utils import generate_otp, store_otp, verify_otp, send_otp_sms
from django.conf import settings
from dotenv import load_dotenv

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

# Load environment variables
load_dotenv()

# Create your views here.


# FireBase
def saveFCMToken(request, token):
    try:
        FCMDevice(token=token).save()
    except:
        pass
    return JsonResponse({})


def showFirebaseJS(request):
    data = f"""
        importScripts('https://www.gstatic.com/firebasejs/11.0.2/firebase-app-compat.js');
        importScripts('https://www.gstatic.com/firebasejs/11.0.2/firebase-messaging-compat.js');

        firebase.initializeApp({{
            apiKey: "{os.getenv('FIREBASE_API_KEY')}",
            authDomain: "{os.getenv('FIREBASE_AUTH_DOMAIN')}",
            projectId: "{os.getenv('FIREBASE_PROJECT_ID')}",
            storageBucket: "{os.getenv('FIREBASE_STORAGE_BUCKET')}",
            messagingSenderId: "{os.getenv('FIREBASE_MESSAGING_SENDER_ID')}",
            appId: "{os.getenv('FIREBASE_APP_ID')}",
            measurementId: "{os.getenv('FIREBASE_MEASUREMENT_ID')}"
        }});

        const messaging = firebase.messaging();

        messaging.onBackgroundMessage((payload) => {{
            const notificationTitle = payload.notification.title;
            const notificationOptions = {{
                body: payload.notification.body,
                icon: payload.notification.icon
            }};

            return self.registration.showNotification(notificationTitle, notificationOptions);
        }});
    """
    return HttpResponse(data, content_type="text/javascript")


@login_required
def dashboard(request):
    """Main dashboard view that redirects to appropriate dashboard based on user role"""
    user = request.user
    user_groups = user.groups.values_list("name", flat=True)

    # Redirect based on user role
    if "Student" in user_groups:
        return redirect("studentDashboard")
    elif "Teacher" in user_groups:
        return redirect("teacherDashboard")

    # Get current date and date ranges
    today = timezone.now().date()
    last_week = timezone.now() - timedelta(days=7)
    last_month = timezone.now() - timedelta(days=30)

    # Student Statistics
    total_students = Student.objects.count()
    active_students = Student.objects.filter(status="Active").count()
    completed_students = Student.objects.filter(status="Completed").count()
    on_leave_students = Student.objects.filter(status="Leave").count()

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
                "description": f"{leave.student.name} requested leave for {leave.date}",
                "timestamp": leave.created_at,
            }
        )

    for leave in recent_staff_leaves:
        recent_activities.append(
            {
                "title": f"Staff Leave Request",
                "description": f"{leave.staff.name} requested leave for {leave.date}",
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


@login_required
def update_profile(request):
    if request.method == "POST":
        user = request.user
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        gender = request.POST.get("gender")
        dob = request.POST.get("dob")

        # Validate data
        if not all([name, email, phone]):
            messages.error(request, "Name, email and phone are required fields.")
            return redirect("studentDashboard")

        # Update profile based on user type
        try:
            if hasattr(user, "student"):
                student = user
                student.name = name
                student.email = email
                student.phone = phone
                student.address = address
                student.gender = gender
                if dob:
                    student.dob = dob

                # Handle profile image
                if "profile_image" in request.FILES:
                    image = request.FILES["profile_image"]
                    if student.image:
                        # Delete old image if updating
                        if os.path.isfile(student.image.path):
                            os.remove(student.image.path)

                    # Save new image
                    student.image = image

                student.save()
                messages.success(request, "Profile updated successfully.")

            elif hasattr(user, "staff"):
                staff = user
                staff.name = name
                staff.email = email
                staff.phone = phone
                staff.address = address
                staff.gender = gender
                if dob:
                    staff.dob = dob

                # Handle profile image
                if "profile_image" in request.FILES:
                    image = request.FILES["profile_image"]
                    if staff.image:
                        # Delete old image if updating
                        if os.path.isfile(staff.image.path):
                            os.remove(staff.image.path)

                    # Save new image
                    staff.image = image

                staff.save()
                messages.success(request, "Profile updated successfully.")

            else:
                messages.error(request, "User profile not found.")

        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")

        # Redirect based on user type
        if hasattr(user, "student"):
            return redirect("studentDashboard")
        elif hasattr(user, "staff"):
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

        # Validate input
        if not all([current_password, new_password, confirm_password]):
            messages.error(request, "All password fields are required.")
            return redirect("studentDashboard")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("studentDashboard")

        # Check current password
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("studentDashboard")

        # Set new password
        try:
            user.set_password(new_password)
            user.save()
            messages.success(
                request, "Password changed successfully. Please login again."
            )
            return redirect("login")
        except Exception as e:
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



