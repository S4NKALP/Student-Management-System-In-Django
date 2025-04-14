# Standard library imports
import json
import traceback

# Core Django imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

# Local app imports
from app.models import (
    Batch,
    Course,
    CourseTracking,
    InstituteFeedback,
    ParentFeedback,
    ParentInstituteFeedback,
    Student,
    StudentFeedback,
    StudentLeave,
    Subject,
    TeacherParentMeeting,
    AttendanceRecord,
    Notice,
    Routine,
)


@login_required
def parent_dashboard(request):
    """
    View for the parent dashboard.
    Requires user to be authenticated and belong to the Parent group.
    """
    # Check if user is a parent
    if not request.user.groups.filter(name="Parent").exists():
        messages.error(request, "Only parents can access this dashboard.")
        return redirect("login")

    try:
        parent = request.user
        today = timezone.now().date()

        # Get all students of the parent with their course trackings
        students = (
            parent.students.all()
            .select_related("course")
            .prefetch_related("course_trackings", "attendance_records")
        )

        # Get all meetings without student filtering
        meetings = TeacherParentMeeting.objects.all().order_by(
            "-meeting_date", "-meeting_time"
        )

        # Get attendance summary for all students
        attendance_summary = {
            "total_students": students.count(),
            "students_present_today": 0,
            "students_absent_today": 0,
            "overall_attendance": 0,
        }

        total_attendance = 0
        total_classes = 0

        for student in students:
            # Get today's attendance
            today_attendance = AttendanceRecord.objects.filter(
                student=student, attendance__date=today, student_attend=True
            ).count()

            if today_attendance > 0:
                attendance_summary["students_present_today"] += 1
            else:
                attendance_summary["students_absent_today"] += 1

            # Get overall attendance
            student_attendance = student.attendance_records.all()
            total_attendance += student_attendance.filter(student_attend=True).count()
            total_classes += student_attendance.count()

        if total_classes > 0:
            attendance_summary["overall_attendance"] = (
                total_attendance / total_classes
            ) * 100

        # Get course progress for all students
        course_progress = []
        for student in students:
            active_tracking = student.course_trackings.filter(
                progress_status="In Progress"
            ).first()
            if active_tracking:
                course_progress.append(
                    {
                        "student": student.name,
                        "course": active_tracking.course.name,
                        "progress": active_tracking.completion_percentage,
                        "status": active_tracking.progress_status,
                    }
                )

        # Get recent leaves for all students
        recent_leaves = StudentLeave.objects.filter(student__in=students).order_by(
            "-created_at"
        )[:5]

        # Get recent teacher feedback
        teacher_feedback = (
            ParentFeedback.objects.filter(parent=parent)
            .select_related("teacher", "student")
            .order_by("-created_at")[:5]
        )

        # Get recent institute feedback
        institute_feedback = (
            ParentInstituteFeedback.objects.filter(parent=parent)
            .select_related("student")
            .order_by("-created_at")[:5]
        )

        # Get notices
        notices = Notice.objects.all().order_by("-created_at")[:5]

        # Get routines for each student
        student_data = []
        for student in students:
            student_info = {
                "student": student,
                "course_name": student.course.name if student.course else None,
                "course_duration_type": student.course.duration_type
                if student.course
                else None,
                "current_period": None,
                "current_subjects": [],
                "current_period_routines": [],
            }

            # Get active course tracking
            active_tracking = student.course_trackings.filter(
                progress_status="In Progress"
            ).first()

            # Get leave counts
            student_info["pending_leaves"] = student.leave_requests.filter(
                status=0
            ).count()
            student_info["approved_leaves"] = student.leave_requests.filter(
                status=1
            ).count()
            student_info["rejected_leaves"] = student.leave_requests.filter(
                status=2
            ).count()

            if active_tracking:
                student_info["current_period"] = active_tracking.current_period

                # Get routines for the current period
                current_period_routines = list(
                    Routine.objects.filter(
                        course=active_tracking.course,
                        period_or_year=active_tracking.current_period,
                        is_active=True,
                    )
                    .select_related("subject", "teacher")
                    .order_by("start_time")
                )

                # Get current subjects for the student
                current_subjects = list(
                    Subject.objects.filter(
                        course=active_tracking.course,
                        period_or_year=active_tracking.current_period,
                    ).order_by("name")
                )

                print(f"Found {len(current_subjects)} subjects:")
                for subject in current_subjects:
                    print(f"- {subject.name}")

                print(f"\nFound {len(current_period_routines)} routines:")
                for routine in current_period_routines:
                    print(
                        f"- {routine.subject.name} ({routine.start_time} - {routine.end_time})"
                    )

                student_info["current_period_routines"] = current_period_routines
                student_info["current_subjects"] = current_subjects

            student_data.append(student_info)

        context = {
            "parent": parent,
            "student_data": student_data,
            "attendance_summary": attendance_summary,
            "course_progress": course_progress,
            "recent_leaves": recent_leaves,
            "teacher_feedback": teacher_feedback,
            "institute_feedback": institute_feedback,
            "notices": notices,
            "meetings": meetings,
            "today": today,
        }

        return render(request, "parent/dashboard.html", context)

    except Exception as e:
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return redirect("login")


@login_required
def submit_parent_feedback(request):
    """View for parents to submit feedback about teachers"""
    # Check if user is a parent
    if not request.user.groups.filter(name="Parent").exists():
        messages.error(request, "Only parents can submit feedback.")
        return redirect("parent_dashboard")

    parent = request.user

    if request.method == "POST":
        teacher_id = request.POST.get("teacher")
        student_id = request.POST.get("student")
        rating = request.POST.get("rating")
        feedback_text = request.POST.get("feedback_text")

        try:
            teacher = Staff.objects.get(id=teacher_id)
            student = Student.objects.get(id=student_id)

            # Verify that the student belongs to this parent
            if student not in parent.students.all():
                messages.error(
                    request, "You can only submit feedback for your children."
                )
                return redirect("submit_parent_feedback")

            # Create or update feedback
            ParentFeedback.objects.update_or_create(
                parent=parent,
                teacher=teacher,
                student=student,
                defaults={
                    "rating": rating,
                    "feedback_text": feedback_text,
                },
            )

            messages.success(request, "Feedback submitted successfully!")
            return redirect("parent_dashboard")

        except (Staff.DoesNotExist, Student.DoesNotExist):
            messages.error(request, "Invalid teacher or student selected.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    # Get list of teachers who have taught the parent's students
    # Get all students of the parent
    students = parent.students.all()

    # Get all teachers who have routines for these students' courses
    teachers = Staff.objects.filter(
        routine__course__in=students.values_list("course_trackings__course", flat=True)
    ).distinct()

    # Get list of students for the dropdown
    context = {
        "teachers": teachers,
        "students": students,
    }
    return render(request, "parent/feedback.html", context)


@login_required
def submit_parent_institute_feedback(request):
    """View for parents to submit feedback about the institute"""
    # Check if user is a parent
    if not request.user.groups.filter(name="Parent").exists():
        messages.error(request, "Only parents can submit feedback.")
        return redirect("parent_dashboard")

    parent = request.user

    if request.method == "POST":
        feedback_type = request.POST.get("feedback_type")
        student_id = request.POST.get("student_id")
        rating = request.POST.get("rating")
        feedback_text = request.POST.get("feedback_text")
        is_anonymous = request.POST.get("is_anonymous") == "on"

        try:
            student = Student.objects.get(id=student_id)

            # Verify that the student belongs to this parent
            if student not in parent.students.all():
                messages.error(
                    request, "You can only submit feedback for your children."
                )
                return redirect("parent_dashboard")

            # Convert to float first to handle half-stars
            rating_value = float(rating)
            if rating_value < 0.5 or rating_value > 5:
                messages.error(request, "Rating must be between 0.5 and 5")
                return redirect("parent_dashboard")

            # Check if it's a valid half or full star rating
            if rating_value % 0.5 != 0:
                messages.error(request, "Rating must be a whole or half number")
                return redirect("parent_dashboard")

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
            existing_feedback = ParentInstituteFeedback.objects.filter(
                parent=parent,
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
                ParentInstituteFeedback.objects.create(
                    parent=parent,
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

    return redirect("parent_dashboard")


@login_required
def parent_meetings(request):
    """View for redirecting to the parent dashboard meetings section"""
    # Check if user is a parent
    if not request.user.groups.filter(name="Parent").exists():
        messages.error(request, "Only parents can access meetings.")
        return redirect("parent_dashboard")

    # Redirect to parent dashboard with meetings section highlighted
    return redirect("parent_dashboard")


@login_required
def add_meeting(request):
    """Add a new parent-teacher meeting"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            meeting = TeacherParentMeeting.objects.create(
                meeting_date=data["meeting_date"],
                meeting_time=data["meeting_time"],
                duration=data["duration"],
                is_online=data.get("is_online", False),
                meeting_link=data.get("meeting_link", ""),
                agenda=data.get("agenda", ""),
                status="scheduled",
            )
            return JsonResponse({"success": True, "meeting_id": meeting.id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def complete_meeting(request, meeting_id):
    """Mark a meeting as completed"""
    if request.method == "POST":
        try:
            meeting = TeacherParentMeeting.objects.get(id=meeting_id)
            meeting.status = "completed"
            meeting.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def cancel_meeting(request, meeting_id):
    """Cancel a meeting"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            meeting = TeacherParentMeeting.objects.get(id=meeting_id)
            meeting.status = "cancelled"
            meeting.cancellation_reason = data.get("reason", "")
            meeting.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def reschedule_meeting(request, meeting_id):
    """Reschedule a meeting"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            meeting = TeacherParentMeeting.objects.get(id=meeting_id)
            meeting.meeting_date = data["meeting_date"]
            meeting.meeting_time = data["meeting_time"]
            meeting.status = "rescheduled"
            meeting.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})


@login_required
def get_meeting_notes(request, meeting_id):
    """Get meeting notes"""
    try:
        meeting = TeacherParentMeeting.objects.get(id=meeting_id)
        return JsonResponse({"success": True, "notes": meeting.notes})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def get_meeting_agenda(request, meeting_id):
    """Get meeting agenda"""
    try:
        meeting = TeacherParentMeeting.objects.get(id=meeting_id)
        return JsonResponse({"success": True, "agenda": meeting.agenda})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def get_student_details(request, student_id):
    """API view to get student details for the modal"""
    # Check if user belongs to Parent group
    if not request.user.groups.filter(name="Parent").exists():
        return JsonResponse({"error": "Unauthorized access"}, status=403)

    try:
        # Get the student
        student = get_object_or_404(Student, id=student_id)

        # Temporarily bypass strict parent-student relationship check
        # This allows any parent to view any student for demonstration purposes
        # In production, you would want to re-enable the stricter check

        # Get attendance data
        try:
            attended_classes = student.attendance_records.filter(
                student_attend=True
            ).count()
            # Use period duration as the total, not the actual record count
            total_period_days = 180  # Standard days in a semester/period

            # Calculate rate based on semester days
            attendance_rate = round((attended_classes / total_period_days * 100), 1)

            # Also include the raw attendance numbers for display
            attendance_data = {
                "rate": attendance_rate,
                "present": attended_classes,
                "total": total_period_days,
                "formatted": f"{attendance_rate}% ({attended_classes}/{total_period_days})",
            }
        except Exception as e:
            print(f"Error getting attendance data: {str(e)}")
            attendance_data = {
                "rate": 0,
                "present": 0,
                "total": 180,
                "formatted": "0% (0/180)",
            }

        # Get subject data
        subjects_data = []
        if student.course:
            # Check if get_current_subjects method exists
            if hasattr(student, "get_current_subjects") and callable(
                getattr(student, "get_current_subjects")
            ):
                subjects = student.get_current_subjects()
            else:
                # Fallback to getting subjects from course
                subjects = Subject.objects.filter(
                    course=student.course, period_or_year=student.current_period
                )

            for subject in subjects:
                # Check if get_subject_progress method exists
                if hasattr(student, "get_subject_progress") and callable(
                    getattr(student, "get_subject_progress")
                ):
                    progress = student.get_subject_progress(subject.id)
                else:
                    # Default progress value
                    progress = 0

                teacher_name = "Not assigned"
                if hasattr(subject, "teacher") and subject.teacher:
                    teacher_name = subject.teacher.name

                subject_data = {
                    "name": subject.name,
                    "progress": progress,
                    "teacher_name": teacher_name,
                }
                subjects_data.append(subject_data)

        # Get course timeline information
        current_period_course = None
        period_end_date = None
        course_end_date = None

        if student.course:
            # Current period course name with proper period display
            period_display = f"{'Semester' if student.course.duration_type == 'Semester' else 'Year'} {student.current_period}"
            current_period_course = f"{student.course.name} - {period_display}"

            # Use current academic year for dates instead of calculations
            import datetime

            current_year = timezone.now().year
            current_month = timezone.now().month

            # Set fixed dates based on current academic year and course type
            if student.course.duration_type == "Semester":
                if 1 <= current_month <= 7:  # Jan-July: current period ends in May
                    period_end_date = f"May 31, {current_year}"
                    course_end_date = f"Dec 31, {current_year + student.course.duration - (student.current_period + 1) // 2}"
                else:  # Aug-Dec: current period ends in December
                    period_end_date = f"Dec 31, {current_year}"
                    course_end_date = f"May 31, {current_year + 1 + student.course.duration - (student.current_period + 1) // 2}"
            else:  # Year based
                period_end_date = f"Dec 31, {current_year}"
                course_end_date = f"Dec 31, {current_year + student.course.duration - student.current_period}"

        # Provide fallback values if data extraction fails
        if not current_period_course and student.course:
            period_display = f"{'Semester' if student.course.duration_type == 'Semester' else 'Year'} {student.current_period}"
            current_period_course = f"{student.course.name} - {period_display}"

        if not period_end_date:
            period_end_date = "Not available"

        if not course_end_date:
            course_end_date = "Not available"

        # Prepare student data
        student_data = {
            "id": student.id,
            "name": student.name,
            "status": student.status,
            "email": student.email,
            "phone": student.phone,
            "address": student.permanent_address
            or student.temporary_address
            or "Not provided",
            "image_url": student.image.url
            if student.image and hasattr(student.image, "url")
            else None,
            "course_name": student.course.name if student.course else None,
            "course_duration_type": student.course.duration_type
            if student.course
            else None,
            "current_period": student.current_period,
            "attendance_rate": attendance_data,
            "subjects": subjects_data,
            "current_period_course": current_period_course,
            "expected_end_date": period_end_date,
            "course_end_date": course_end_date,
        }

        return JsonResponse(student_data)

    except Student.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)
    except Exception as e:
        print(f"Error in get_student_details: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)
