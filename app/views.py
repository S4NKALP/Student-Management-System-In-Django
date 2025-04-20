from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from app.models import (
    Student,
    Course,
    CourseTracking,
    StudentLeave,
    StaffLeave,
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
    ParentFeedback,
    Parent,
    StaffInstituteFeedback,
    ParentInstituteFeedback,
    TeacherParentMeeting,
)
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
from app.admin import custom_admin_site
import os
from django.db.models.base import transaction
from dotenv import load_dotenv
from app.firebase import save_fcm_token, FCMDevice
from django.views.static import serve

# Import views from studentviews.py
from app.studentviews import (
    studentDashboard,
    request_leave,
    submit_feedback,
    submit_institute_feedback,
    get_subject_files,
)

# Import views from staffviews.py
from app.staffviews import (
    teacherDashboard,
    request_staff_leave,
    submit_staff_institute_feedback,
    save_attendance,
    get_subject_schedule,
    teacher_update_profile_picture,
    teacher_change_password,
)

from django.contrib.auth.hashers import check_password
from django.urls import reverse

# Load environment variables
load_dotenv()

# Create your views here.


@login_required
def dashboard(request):
    """Main dashboard view that redirects to appropriate dashboard based on user role.

    Args:
        request: HttpRequest object containing user information

    Returns:
        HttpResponse: Redirects to appropriate dashboard or renders admin dashboard
    """
    user = request.user
    user_groups = user.groups.values_list("name", flat=True)

    # Redirect based on user role
    if "Student" in user_groups:
        return redirect("studentDashboard")
    elif "Teacher" in user_groups:
        return redirect("teacherDashboard")
    elif "Parent" in user_groups:
        return redirect("parentDashboard")
    elif "Admission Officer" in user_groups:
        return redirect("admissionOfficerDashboard")
    elif "HOD" in user_groups:
        return redirect("hodDashboard")
    else:
        # Get current date and date ranges
        today = timezone.now().date()
        last_week = timezone.now() - timedelta(days=7)
        last_month = timezone.now() - timedelta(days=30)

        # Student Statistics
        total_students = Student.objects.count()
        active_students = Student.objects.filter(status="Active").count()
        male_students = Student.objects.filter(gender="Male").count()
        female_students = Student.objects.filter(gender="Female").count()
        inactive_students = total_students - active_students

        # Staff Statistics
        total_staff = Staff.objects.count()
        active_staff = Staff.objects.filter(is_active=True).count()
        total_teachers = Staff.objects.filter(designation="Teacher").count()
        non_teaching_staff = total_staff - total_teachers
        inactive_staff = total_staff - active_staff

        # Parent Statistics
        total_parents = Parent.objects.count()
        active_parents = Parent.objects.filter(is_active=True).count()
        parents_with_students = (
            Parent.objects.filter(students__isnull=False).distinct().count()
        )
        parents_with_multiple_students = (
            Parent.objects.annotate(student_count=Count("students"))
            .filter(student_count__gt=1)
            .count()
        )
        inactive_parents = total_parents - active_parents

        # Course Statistics
        total_courses = Course.objects.count()
        active_courses = (
            Course.objects.filter(
                student_trackings__progress_status__in=["Not Started", "In Progress"]
            )
            .distinct()
            .count()
        )
        total_subjects = Subject.objects.count()
        total_batches = Batch.objects.count()
        inactive_courses = total_courses - active_courses

        # Recent Activities
        recent_notices = Notice.objects.all().order_by("-created_at")[:5]
        recent_feedback = (
            list(InstituteFeedback.objects.all().order_by("-created_at")[:5])
            + list(StaffInstituteFeedback.objects.all().order_by("-created_at")[:5])
            + list(ParentInstituteFeedback.objects.all().order_by("-created_at")[:5])
        )
        recent_feedback = sorted(
            recent_feedback, key=lambda x: x.created_at, reverse=True
        )[:5]

        # Leave Requests
        staff_leaves = StaffLeave.objects.filter(status=0).order_by("-created_at")[
            :5
        ]  # 0 = Pending
        student_leaves = StudentLeave.objects.filter(status=0).order_by("-created_at")[
            :5
        ]  # 0 = Pending

        # Teacher Rating Statistics
        teacher_ratings = (
            Staff.objects.filter(designation="Teacher")
            .annotate(
                avg_student_rating=Avg("feedbacks__rating"),
                avg_parent_rating=Avg("parent_feedbacks__rating"),
                total_feedbacks=Count("feedbacks") + Count("parent_feedbacks"),
            )
            .order_by("-avg_student_rating")[:5]
        )

        # Get all meetings
        meetings = TeacherParentMeeting.objects.all().order_by(
            "-meeting_date", "-meeting_time"
        )

        context = {
            "title": "Dashboard",
            **custom_admin_site.each_context(request),
            "total_students": total_students,
            "active_students": active_students,
            "male_students": male_students,
            "female_students": female_students,
            "inactive_students": inactive_students,
            "total_staff": total_staff,
            "active_staff": active_staff,
            "total_teachers": total_teachers,
            "non_teaching_staff": non_teaching_staff,
            "inactive_staff": inactive_staff,
            "total_parents": total_parents,
            "active_parents": active_parents,
            "parents_with_students": parents_with_students,
            "parents_with_multiple_students": parents_with_multiple_students,
            "inactive_parents": inactive_parents,
            "total_courses": total_courses,
            "active_courses": active_courses,
            "total_subjects": total_subjects,
            "total_batches": total_batches,
            "inactive_courses": inactive_courses,
            "recent_notices": recent_notices,
            "recent_feedback": recent_feedback,
            "staff_leaves": staff_leaves,
            "student_leaves": student_leaves,
            "teacher_ratings": teacher_ratings,
            "meetings": meetings,
        }

        return render(request, "admin/dashboard.html", context)


@login_required
def update_profile(request):
    """Update user profile picture based on user role.

    Args:
        request: HttpRequest object containing user information and uploaded file

    Returns:
        HttpResponse: Redirects to appropriate dashboard with success/error message
    """
    if request.method == "POST":
        user = request.user
        user_groups = user.groups.values_list("name", flat=True)

        # Handle profile image update
        if "profile_image" in request.FILES:
            try:
                image = request.FILES["profile_image"]

                # Validate image file type
                allowed_types = ["image/jpeg", "image/png", "image/gif"]
                if image.content_type not in allowed_types:
                    messages.error(
                        request,
                        "Invalid file type. Please upload a JPEG, PNG, or GIF image.",
                    )
                    return redirect("dashboard")

                # Validate image size (max 5MB)
                if image.size > 5 * 1024 * 1024:
                    messages.error(
                        request,
                        "Image size too large. Please upload an image smaller than 5MB.",
                    )
                    return redirect("dashboard")

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

                elif "Parent" in user_groups:
                    parent = Parent.objects.get(id=user.id)
                    if parent.image:
                        # Delete old image if updating
                        if os.path.isfile(parent.image.path):
                            os.remove(parent.image.path)
                    # Save new image
                    parent.image = image
                    parent.save()
                    messages.success(request, "Profile picture updated successfully.")

                elif "HOD" in user_groups or any(
                    group.lower().startswith("hod") for group in user_groups
                ):
                    # HOD is typically a Staff member with special privileges
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
                    messages.error(
                        request,
                        "User profile not found. Please make sure you are logged in as a student, staff, or parent member.",
                    )
                    return redirect("dashboard")

            except (Student.DoesNotExist, Staff.DoesNotExist, Parent.DoesNotExist) as e:
                messages.error(request, "User profile not found in the database.")
                return redirect("dashboard")
            except Exception as e:
                messages.error(request, f"Error updating profile picture: {str(e)}")
                return redirect("dashboard")
        else:
            messages.error(request, "No profile picture uploaded.")
            return redirect("dashboard")

        # Redirect based on user type
        if "Student" in user_groups:
            return redirect("studentDashboard")
        elif "Teacher" in user_groups:
            return redirect("teacherDashboard")
        elif "Parent" in user_groups:
            return redirect("parentDashboard")
        elif "Admission Officer" in user_groups:
            return redirect("admissionOfficerDashboard")
        elif "HOD" in user_groups:
            return redirect("hodDashboard")
        else:
            return redirect("dashboard")

    return redirect("dashboard")


@login_required
def change_password(request):
    if request.method == "POST":
        user = request.user
        user_groups = user.groups.values_list("name", flat=True)
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Check if this is an AJAX request
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        # Determine redirect URL based on user role
        redirect_url = "dashboard"
        if "Student" in user_groups:
            redirect_url = "studentDashboard"
        elif "Teacher" in user_groups:
            redirect_url = "teacherDashboard"
        elif "Parent" in user_groups:
            redirect_url = "parentDashboard"
        elif "Admission Officer" in user_groups:
            redirect_url = "admissionOfficerDashboard"
        elif "HOD" in user_groups:
            redirect_url = "hodDashboard"

        # Validate input
        if not all([current_password, new_password, confirm_password]):
            if is_ajax:
                return JsonResponse(
                    {"success": False, "error": "All password fields are required."}
                )
            messages.error(request, "All password fields are required.")
            return redirect(redirect_url)

        if new_password != confirm_password:
            if is_ajax:
                return JsonResponse(
                    {"success": False, "error": "New passwords do not match."}
                )
            messages.error(request, "New passwords do not match.")
            return redirect(redirect_url)

        # Check current password
        if not user.check_password(current_password):
            if is_ajax:
                return JsonResponse(
                    {"success": False, "error": "Current password is incorrect."}
                )
            messages.error(request, "Current password is incorrect.")
            return redirect(redirect_url)

        # Set new password
        try:
            user.set_password(new_password)
            user.save()

            # For both AJAX and regular requests, we'll return success and indicate need for logout
            if is_ajax:
                return JsonResponse(
                    {
                        "success": True,
                        "redirect": "/login/",
                        "message": "Password changed successfully. Please login again.",
                    }
                )

            messages.success(
                request, "Password changed successfully. Please login again."
            )
            return redirect("login")

        except Exception as e:
            if is_ajax:
                return JsonResponse(
                    {"success": False, "error": f"Error changing password: {str(e)}"}
                )
            messages.error(request, f"Error changing password: {str(e)}")
            return redirect(redirect_url)

    return redirect("dashboard")


@login_required
@require_GET
def get_subjects(request):
    """Get subjects for a course and period"""
    course_id = request.GET.get("course_id")
    period = request.GET.get("period", 1)

    if not course_id:
        return JsonResponse({"success": False, "message": "Course ID is required"})

    try:
        subjects = Subject.objects.filter(
            course_id=course_id, period_or_year=period
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
            | Q(designation__icontains="HOD")
            | Q(designation__icontains="Admission Officer")
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
        leave = get_object_or_404(StudentLeave, id=leave_id)
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
        leave = get_object_or_404(StudentLeave, id=leave_id)
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
        leave = get_object_or_404(StaffLeave, id=leave_id)
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
        leave = get_object_or_404(StaffLeave, id=leave_id)
        leave.status = 2  # Rejected
        leave.save()
        messages.warning(
            request, f"Leave request for {leave.staff.name} has been rejected."
        )
    return redirect("dashboard")


@login_required
def add_notice(request):
    if request.method == "POST":
        try:
            title = request.POST.get("title")
            message = request.POST.get("message")
            image = request.FILES.get("image")

            if not title or not message:
                return JsonResponse(
                    {"success": False, "error": "Title and message are required"}
                )

            notice = Notice.objects.create(title=title, message=message, image=image)

            return JsonResponse(
                {"success": True, "message": "Notice added successfully"}
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})


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
@require_POST
def save_fcm_token(request):
    try:
        print("Received FCM token save request")
        data = json.loads(request.body)
        token = data.get("token")
        timestamp = data.get("timestamp")
        vapid_key_used = data.get("vapidKeyUsed", False)

        # Log additional information for debugging
        auth_header = request.headers.get("Authorization", "")
        using_vapid_auth = auth_header.startswith("VAPID ")

        print(f"Auth method: {'VAPID' if using_vapid_auth else 'Cookie-based'}")
        print(f"VAPID key used for token generation: {vapid_key_used}")

        if not token:
            print("No token provided in request")
            return JsonResponse({"error": "Token is required"}, status=400)

        user = request.user
        print(f"User authenticated: {user.id} ({user.username})")
        user_groups = user.groups.values_list("name", flat=True)

        print(f"FCM token saving for user: {user.id}, groups: {list(user_groups)}")

        # Determine user type based on group membership
        user_type = "unknown"
        if user.is_superuser:
            user_type = "admin"
        elif "Student" in user_groups:
            user_type = "student"
        elif "Teacher" in user_groups:
            user_type = "teacher"
        elif "Parent" in user_groups:
            user_type = "parent"

        # Save token directly to the user model
        user.fcm_token = token
        user.save(update_fields=["fcm_token"])
        print(f"FCM token saved directly to user {user.name}")

        # Update or create FCMDevice
        try:
            # Check if this is a fallback token
            is_fallback = token.startswith("fcm-token-") or token.startswith(
                "fallback-token-"
            )

            # Create or update the device
            device, created = FCMDevice.objects.update_or_create(
                token=token,
                defaults={
                    "is_active": True,
                    "is_fallback": is_fallback,
                    "user_type": user_type,
                },
            )

            print(
                f"FCMDevice {'created' if created else 'updated'} with ID: {device.id}, user_type: {user_type}"
            )
        except Exception as e:
            print(f"Error creating/updating FCMDevice: {str(e)}")
            raise

        return JsonResponse(
            {
                "status": "success",
                "device_id": device.id,
                "created": created,
                "auth_method": "vapid" if using_vapid_auth else "cookie",
                "user_type": user_type,
            }
        )
    except json.JSONDecodeError:
        print("Invalid JSON in request body")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        print(f"Error in save_fcm_token: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


def serve_firebase_sw(request):
    """Serve the Firebase service worker file with correct content type and security headers"""
    try:
        # Get the path to the service worker in the static directory
        sw_path = os.path.join(settings.STATICFILES_DIRS[0], "firebase-messaging-sw.js")

        # If the file doesn't exist in static directory, try staticfiles
        if not os.path.exists(sw_path):
            sw_path = os.path.join(settings.STATIC_ROOT, "firebase-messaging-sw.js")

        if not os.path.exists(sw_path):
            print(f"Service worker file not found at: {sw_path}")
            return HttpResponse("Service worker file not found", status=404)

        with open(sw_path, "r") as f:
            content = f.read()

        # Create response with correct content type
        response = HttpResponse(content, content_type="application/javascript")

        # Set all necessary security headers for service worker
        response["Service-Worker-Allowed"] = "/"
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"

        # Set proper CORS headers for service worker
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"

        print(f"Serving service worker file successfully, size: {len(content)}")
        return response
    except Exception as e:
        print(f"Error serving service worker: {str(e)}")
        return HttpResponse("Internal server error", status=500)


@login_required
def check_weak_password(request):
    """Check if the current user's password is '123'"""
    user = request.user
    is_weak = check_password("123", user.password)
    return JsonResponse({"is_weak": is_weak})


@login_required
def get_staff_leaves(request):
    """View to get staff leave requests for AJAX updates"""
    staff_leaves = StaffLeave.objects.filter(status=0).order_by("-created_at")[:5]
    leaves_data = []
    for leave in staff_leaves:
        leaves_data.append(
            {
                "id": leave.id,
                "staff_name": leave.staff.name,
                "start_date": leave.start_date.strftime("%b %d, %Y"),
                "end_date": leave.end_date.strftime("%b %d, %Y"),
                "message": leave.message[:50] + "..."
                if len(leave.message) > 50
                else leave.message,
            }
        )
    return JsonResponse({"staff_leaves": leaves_data})


@login_required
def get_student_leaves(request):
    """View to get student leave requests for AJAX updates"""
    student_leaves = StudentLeave.objects.filter(status=0).order_by("-created_at")[:5]
    leaves_data = []
    for leave in student_leaves:
        leaves_data.append(
            {
                "id": leave.id,
                "student_name": leave.student.name,
                "start_date": leave.start_date.strftime("%b %d, %Y"),
                "end_date": leave.end_date.strftime("%b %d, %Y"),
                "message": leave.message[:50] + "..."
                if len(leave.message) > 50
                else leave.message,
            }
        )
    return JsonResponse({"student_leaves": leaves_data})


@login_required
@require_GET
def get_meeting_cancellation_reason(request, meeting_id):
    """API endpoint to get the cancellation reason for a meeting"""
    try:
        meeting = get_object_or_404(TeacherParentMeeting, id=meeting_id)

        if meeting.status != "cancelled":
            return JsonResponse({"success": False, "error": "Meeting is not cancelled"})

        return JsonResponse({"success": True, "reason": meeting.cancellation_reason})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
