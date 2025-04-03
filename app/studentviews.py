from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_http_methods, require_GET
from .models import (
    Student,
    Course,
    CourseTracking,
    Student_Leave,
    Staff,
    Attendance,
    AttendanceRecord,
    StudentFeedback,
    Routine,
    Notice,
    Institute,
    InstituteFeedback,
    Subject,
    FEEDBACK_TYPE_CHOICES,
)


@login_required
def studentDashboard(request):
    """View to display the student dashboard with their personal information and progress"""
    student = Student.objects.get(phone=request.user.phone)  # Get the Student object
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    # Clear section states on page load
    if request.method == 'GET':
        request.session.pop('active_section', None)
        request.session.pop('active_subsection', None)

    # Get all teachers for feedback form
    teachers = Staff.objects.filter(
        Q(designation__icontains="Teacher")
        | Q(designation__icontains="Staff")
        | Q(designation__icontains="Principal")
        | Q(designation__isnull=True)
        | Q(designation="")
    ).order_by("name")

    # Get feedback types for institute feedback
    feedback_types = FEEDBACK_TYPE_CHOICES

    # Course Progress and Tracking
    course_trackings = CourseTracking.objects.filter(student=student).select_related(
        "course"
    )
    total_courses = course_trackings.count()
    completed_courses = course_trackings.filter(progress_status="Completed").count()
    in_progress_courses = course_trackings.filter(progress_status="In Progress").count()
    dropped_courses = course_trackings.filter(progress_status="Dropped").count()

    # Calculate overall completion percentage
    overall_completion = 0
    if total_courses > 0:
        total_percentage = sum(
            tracking.completion_percentage for tracking in course_trackings
        )
        overall_completion = total_percentage / total_courses

    # Course Summary
    course_summary = {
        "total_courses": total_courses,
        "completed_courses": completed_courses,
        "ongoing_courses": in_progress_courses,
        "completion_percentage": overall_completion,
    }

    # Course Details with enhanced information
    course_details = []
    for tracking in course_trackings:
        course_details.append({
            "name": tracking.course.name,
            "start_date": tracking.start_date,
            "expected_end_date": tracking.expected_end_date,
            "actual_end_date": tracking.actual_end_date,
            "completion_percentage": tracking.completion_percentage,
            "progress_status": tracking.progress_status,
            "current_semester": tracking.current_semester,
            "semester_start_date": tracking.semester_start_date,
            "semester_end_date": tracking.semester_end_date,
            "remaining_days": tracking.remaining_days,
            "is_completed": tracking.is_completed,
            "is_active": tracking.is_active,
            "duration_type": tracking.course.duration_type,
            "duration": tracking.course.duration,
            "total_duration_days": tracking.total_duration_days,
            "notes": tracking.notes,
        })

    # Get current subjects based on current semester
    current_subjects = []
    active_tracking = course_trackings.filter(progress_status="In Progress").first()
    if active_tracking:
        current_subjects = Subject.objects.filter(
            course=active_tracking.course,
            semester_or_year=active_tracking.current_semester
        )

    # Attendance Statistics with enhanced information
    attendance_records = AttendanceRecord.objects.filter(student=student)
    
    # Get the current semester start and end dates from student's course tracking
    current_semester_start = None
    current_semester_end = None
    
    # Try to get course tracking for current student
    try:
        if active_tracking and active_tracking.semester_start_date:
            current_semester_start = active_tracking.semester_start_date
            current_semester_end = active_tracking.semester_end_date or today
    except Exception:
        pass
    
    # Filter attendance by current semester date range if available
    if current_semester_start:
        semester_attendance = attendance_records.filter(
            attendance__date__gte=current_semester_start,
            attendance__date__lte=current_semester_end
        )
        
        # Count the actual classes and attendance
        actual_classes = semester_attendance.count()
        classes_attended = semester_attendance.filter(student_attend=True).count()
        
        # Check if the course is semester-based or year-based
        is_semester_based = active_tracking.course.duration_type == "Semester" if active_tracking else True
            
        # Set the denominator based on semester/year
        if is_semester_based:
            # For a 6-month semester, use 180 days as denominator
            total_classes = 180
        else:
            # For a full year, use 365 days as denominator
            total_classes = 365  # Or use 317 (365 - 48) if excluding Saturdays
        
        # Keep track of actual records for display purposes
        if actual_classes > 0:
            attendance_summary_actual = (classes_attended / actual_classes * 100)
        else:
            attendance_summary_actual = 0
    else:
        # Fall back to overall attendance if semester dates aren't available
        actual_classes = attendance_records.count()
        classes_attended = attendance_records.filter(student_attend=True).count()
        total_classes = 180  # Default to semester-based
        attendance_summary_actual = 0
        
    # Calculate attendance percentage using the fixed formula
    attendance_percentage = (
        (classes_attended / total_classes * 100) if total_classes > 0 else 0
    )

    # Calculate attendance streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    last_attendance_date = None

    for record in attendance_records.order_by("-attendance__date"):
        if record.student_attend:
            if last_attendance_date is None:
                last_attendance_date = record.attendance.date
                current_streak = 1
                temp_streak = 1
            elif (last_attendance_date - record.attendance.date).days == 1:
                temp_streak += 1
                if temp_streak > longest_streak:
                    longest_streak = temp_streak
                if record.attendance.date == today - timedelta(days=current_streak):
                    current_streak += 1
            else:
                temp_streak = 1
        else:
            temp_streak = 0
            if record.attendance.date == today:
                current_streak = 0

    # Attendance Summary
    attendance_summary = {
        "total_classes": total_classes,
        "classes_attended": classes_attended,
        "present_count": classes_attended,
        "absent_count": total_classes - classes_attended,
        "attendance_percentage": attendance_percentage,
        "current_streak": current_streak,
        "longest_streak": longest_streak
    }
    
    # Add actual recorded classes info if different from expected
    if current_semester_start and actual_classes != total_classes:
        attendance_summary["actual_classes"] = actual_classes
        attendance_summary["actual_percentage"] = attendance_summary_actual

    # Get attendance records with related information
    attendance_records = attendance_records.select_related(
        "attendance", "attendance__routine", "attendance__teacher"
    ).order_by("-attendance__date")

    # Get recent attendance (last 7 days)
    recent_attendance = attendance_records.filter(
        attendance__date__gte=last_week
    ).order_by("-attendance__date")

    # Get feedback
    recent_feedback = student.feedbacks.all().order_by("-created_at")[:5]
    institute_feedback = student.institute_feedbacks.all().order_by("-created_at")[:5]

    # Get notices
    notices = Notice.objects.all().order_by("-created_at")

    # Get student leaves with status information
    student_leaves = Student_Leave.objects.filter(student=student).order_by(
        "-created_at"
    )
    pending_leaves = student_leaves.filter(status=0).count()
    approved_leaves = student_leaves.filter(status=1).count()
    rejected_leaves = student_leaves.filter(status=2).count()

    # Get current semester routines
    current_semester_routines = []
    if active_tracking:
        current_semester_routines = Routine.objects.filter(
            course=active_tracking.course,
            semester_or_year=active_tracking.current_semester,
            is_active=True,
        )

    # Check if student has any routines
    has_routines = current_semester_routines.exists()

    context = {
        "student": student,
        "title": "Student Dashboard",
        "teachers": teachers,
        "feedback_types": feedback_types,
        # Course Progress
        "total_courses": total_courses,
        "completed_courses": completed_courses,
        "in_progress_courses": in_progress_courses,
        "dropped_courses": dropped_courses,
        "overall_completion": round(overall_completion, 1),
        "course_details": course_details,
        "course_summary": course_summary,
        # Current Subjects
        "current_subjects": current_subjects,
        # Attendance
        "attendance_summary": attendance_summary,
        "attendance_records": attendance_records,
        "recent_attendance": recent_attendance,
        # Feedback
        "recent_feedback": recent_feedback,
        "institute_feedback": institute_feedback,
        # Notices
        "notices": notices,
        # Leaves
        "student_leaves": student_leaves,
        "pending_leaves": pending_leaves,
        "approved_leaves": approved_leaves,
        "rejected_leaves": rejected_leaves,
        # Routines
        "current_semester_routines": current_semester_routines,
        "has_routines": has_routines,
        # Current date for display
        "today": today,
    }

    return render(request, "student_dashboard.html", context)


@login_required
def request_leave(request):
    if request.method == "POST":
        student = request.user
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        message = request.POST.get("message")

        try:
            # Convert date strings to timezone-aware datetime
            start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d")
            start_date = timezone.make_aware(start_date)
            end_date = timezone.make_aware(end_date)
            today = timezone.now()

            if start_date.date() < today.date():
                messages.error(request, "Start date cannot be in the past.")
                return redirect("studentDashboard")

            if end_date.date() < start_date.date():
                messages.error(request, "End date cannot be before start date.")
                return redirect("studentDashboard")

            # Check if leave already exists for these dates
            existing_leave = Student_Leave.objects.filter(
                student=student,
                start_date__lte=end_date.date(),
                end_date__gte=start_date.date()
            ).first()

            if existing_leave:
                messages.error(
                    request, "You have already requested leave for these dates."
                )
                return redirect("studentDashboard")

            # Create leave request
            leave = Student_Leave.objects.create(
                student=student,
                start_date=start_date.date(),
                end_date=end_date.date(),
                message=message,
                status=0,  # Pending status
            )
            messages.success(request, "Leave request submitted successfully.")
        except Exception as e:
            messages.error(request, f"Error submitting leave request: {str(e)}")

        return redirect("studentDashboard")

    return redirect("studentDashboard")


@login_required
def submit_feedback(request):
    if request.method == "POST":
        try:
            feedback_type = request.POST.get("feedback_type")
            rating = float(request.POST.get("rating", 0))
            feedback_text = request.POST.get("feedback_text", "").strip()

            # Validate rating range (1 to 5)
            if not (1 <= rating <= 5):
                messages.error(request, "Rating must be between 1 and 5")
                return redirect("studentDashboard")

            if not feedback_text:
                messages.error(request, "Please provide feedback text")
                return redirect("studentDashboard")

            if feedback_type == "teacher":
                teacher_id = request.POST.get("teacher_id")
                if not teacher_id:
                    messages.error(request, "Please select a teacher")
                    return redirect("studentDashboard")

                try:
                    teacher = Staff.objects.get(id=teacher_id)
                    # Check if feedback already exists
                    existing_feedback = StudentFeedback.objects.filter(
                        student=request.user, teacher=teacher
                    ).first()

                    if existing_feedback:
                        # Update existing feedback
                        existing_feedback.rating = rating
                        existing_feedback.feedback_text = feedback_text
                        existing_feedback.save()
                        messages.success(request, "Teacher feedback updated successfully")
                    else:
                        # Create new feedback
                        StudentFeedback.objects.create(
                            student=request.user,
                            teacher=teacher,
                            rating=rating,
                            feedback_text=feedback_text,
                        )
                        messages.success(request, "Teacher feedback submitted successfully")

                except Staff.DoesNotExist:
                    messages.error(request, "Selected teacher does not exist")

            else:
                messages.error(request, "Invalid feedback type")

        except ValueError:
            messages.error(request, "Invalid rating value")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return redirect("studentDashboard")


@login_required
def submit_institute_feedback(request):
    if request.method == "POST":
        student = request.user
        feedback_type = request.POST.get("feedback_type")
        rating = request.POST.get("rating")
        feedback_text = request.POST.get("feedback_text")
        is_anonymous = request.POST.get("is_anonymous") == "on"

        try:
            # Validate feedback type
            if not feedback_type or feedback_type not in dict(InstituteFeedback.FEEDBACK_TYPE_CHOICES):
                messages.error(request, "Please select a valid feedback type")
                return redirect("studentDashboard")

            # Convert to float first to handle half-stars
            rating_value = float(rating)
            if rating_value < 0.5 or rating_value > 5:
                messages.error(request, "Rating must be between 0.5 and 5")
                return redirect("studentDashboard")

            # Check if it's a valid half or full star rating
            if rating_value % 0.5 != 0:
                messages.error(request, "Rating must be a whole or half number")
                return redirect("studentDashboard")

            # Get the institute (assuming one institute for now)
            institute = Institute.objects.first()

            if not institute:
                # Create a default institute if none exists
                institute = Institute.objects.create(
                    name="Default Institute",
                    phone="123456789",
                    email="default@example.com",
                )

            # Check if feedback already exists for this type
            existing_feedback = InstituteFeedback.objects.filter(
                user=student,
                institute=institute,
                feedback_type=feedback_type,
            ).first()

            if existing_feedback:
                # Update existing feedback
                existing_feedback.rating = rating_value
                existing_feedback.feedback_text = feedback_text
                existing_feedback.is_anonymous = is_anonymous
                existing_feedback.save()
                messages.success(request, "Institute feedback updated successfully")
            else:
                # Create new feedback
                InstituteFeedback.objects.create(
                    user=student,
                    institute=institute,
                    feedback_type=feedback_type,
                    rating=rating_value,
                    feedback_text=feedback_text,
                    is_anonymous=is_anonymous,
                    is_public=True,  # Default to public feedback
                )
                messages.success(request, "Institute feedback submitted successfully")

        except ValueError:
            messages.error(request, "Invalid rating value")
        except Exception as e:
            messages.error(request, f"Error submitting institute feedback: {str(e)}")

    return redirect("studentDashboard")


@login_required
@require_http_methods(["GET"])
def get_subject_files(request, subject_id):
    """View to get all files for a subject"""
    try:
        subject = Subject.objects.get(id=subject_id)
        files = subject.get_all_files()
        
        if not files:
            return JsonResponse(
                {"success": False, "message": "No files available for this subject"}
            )

        return JsonResponse(
            {
                "success": True,
                "files": files,
            }
        )
    except Subject.DoesNotExist:
        return JsonResponse({"success": False, "message": "Subject not found"})
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Error retrieving files: {str(e)}"}
        )
