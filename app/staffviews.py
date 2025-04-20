from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from django.views.decorators.http import require_http_methods, require_GET
from django.contrib.auth.hashers import check_password, make_password
from app.models import (
    Staff,
    Student,
    Routine,
    Attendance,
    AttendanceRecord,
    StudentFeedback,
    StaffLeave,
    Notice,
    Institute,
    StaffInstituteFeedback,
    Subject,
    SubjectFile,
    InstituteFeedback,
    CourseTracking,
    FEEDBACK_TYPE_CHOICES,
)
import logging


@login_required
def teacherDashboard(request):
    """View to display the teacher dashboard with their classes and student information"""

    # Check if user is in Teacher group
    if not request.user.groups.filter(name="Teacher").exists():
        print(request, "You don't have permission to access the teacher dashboard.")
        return redirect("dashboard")

    # Get or create a teacher object
    try:
        # Try to get the teacher object directly if user is already a Staff instance
        if isinstance(request.user, Staff):
            teacher = request.user
        else:
            # Try to get the staff object by ID
            teacher = Staff.objects.get(id=request.user.id)
    except (Staff.DoesNotExist, Exception) as e:
        print(f"Error getting staff profile: {str(e)}")
        messages.error(
            request, "Teacher profile not found. Please contact administrator."
        )
        return redirect("dashboard")

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

        # Get total active students for this routine - matching the get_students logic
        students = Student.objects.filter(
            course=routine.subject.course,
            current_period=routine.period_or_year,
            status="Active",  # Only count active students
        )

        # If no students found with exact period match, try more flexible approach
        if not students.exists():
            students = Student.objects.filter(
                course=routine.subject.course,
                status="Active",  # Still only count active students
            )

        total_students = students.count()

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
                "id": routine.id,
                "name": routine.subject.name,
                "start_time": routine.start_time,
                "end_time": routine.end_time,
                "is_completed": attendance is not None,
                "is_ongoing": routine.start_time <= current_time <= routine.end_time,
                "total_students": total_students,
                "attendance_count": attendance_count,
                "period_or_year": routine.period_or_year,
                "course_name": routine.subject.course.name,
                "has_attendance": attendance is not None,
                "subject_id": routine.subject.id,
            }
        )

    # Calculate class statistics
    total_classes = today_routines.count()
    completed_classes = len([r for r in processed_routines if r["is_completed"]])
    remaining_classes = total_classes - completed_classes

    # Get student statistics from course tracking
    total_students = (
        CourseTracking.objects.filter(
            course__in=today_routines.values_list("subject__course", flat=True),
            progress_status="In Progress",
        )
        .values("student")
        .distinct()
        .count()
    )

    # Get present and absent students for today
    present_students = (
        AttendanceRecord.objects.filter(
            attendance__date=today,
            student_attend=True,
            attendance__routine__teacher=teacher,
        )
        .values("student")
        .distinct()
        .count()
    )

    # Calculate absent students based on teacher's classes today
    today_class_students = set()
    for routine in today_routines:
        students = CourseTracking.objects.filter(
            course=routine.subject.course,
            current_period=routine.period_or_year,
            progress_status="In Progress",
        ).values_list("student", flat=True)
        today_class_students.update(students)

    # Make sure absent students doesn't go negative
    total_today_students = len(today_class_students)
    absent_students = (
        max(0, total_today_students - present_students) if total_today_students else 0
    )

    # Get average rating from student feedback
    avg_rating = (
        StudentFeedback.objects.filter(teacher=teacher).aggregate(Avg("rating"))[
            "rating__avg"
        ]
        or 0
    )
    avg_rating_rounded = round(avg_rating)
    remaining_stars = 5 - avg_rating_rounded

    # Get leave statistics
    pending_leaves = StaffLeave.objects.filter(staff=teacher, status=0).count()
    approved_leaves = StaffLeave.objects.filter(staff=teacher, status=1).count()
    rejected_leaves = StaffLeave.objects.filter(staff=teacher, status=2).count()

    # Get recent leaves
    recent_leaves = StaffLeave.objects.filter(staff=teacher).order_by("-created_at")[:5]

    # Get recent feedback
    recent_feedback = StudentFeedback.objects.filter(teacher=teacher).order_by(
        "-created_at"
    )[:5]

    # Get notices
    notices = Notice.objects.all().order_by("-created_at")[:5]

    # Get feedback types for institute feedback
    feedback_types = FEEDBACK_TYPE_CHOICES

    # Get institute feedback
    institute_feedback = StaffInstituteFeedback.objects.filter(staff=teacher).order_by(
        "-created_at"
    )[:5]

    # Get all routines for the teacher (for the schedule)
    all_routines = Routine.objects.filter(
        teacher=teacher,
        is_active=True,
        period_or_year__in=CourseTracking.objects.filter(progress_status="In Progress")
        .values_list("current_period", flat=True)
        .distinct(),
    ).order_by("start_time")

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
    routines = Routine.objects.filter(teacher=teacher, is_active=True).order_by(
        "start_time"
    )

    # Get all subjects taught by this teacher for the subjects section
    subject_ids = (
        Routine.objects.filter(teacher=teacher, is_active=True)
        .values_list("subject", flat=True)
        .distinct()
    )

    teacher_subjects = (
        Routine.objects.filter(
            teacher=teacher, is_active=True, subject_id__in=subject_ids
        )
        .select_related("subject", "course")
        .order_by("subject__name")
    )

    # Add student count to each routine
    for routine in teacher_subjects:
        routine.students_count = CourseTracking.objects.filter(
            course=routine.course,
            current_period=routine.period_or_year,
            progress_status="In Progress",
        ).count()

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
        "routines": routines,
        "today": today,
        "teacher_subjects": teacher_subjects,
    }

    return render(request, "teacher/dashboard.html", context)


@login_required
def request_staff_leave(request):
    """View to handle leave requests from staff"""
    if request.method == "POST":
        staff = request.user
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
                return redirect("teacherDashboard")

            if end_date.date() < start_date.date():
                messages.error(request, "End date cannot be before start date.")
                return redirect("teacherDashboard")

            # Check if leave already exists for these dates
            existing_leave = StaffLeave.objects.filter(
                staff=staff,
                start_date__lte=end_date.date(),
                end_date__gte=start_date.date(),
            ).first()

            if existing_leave:
                messages.error(
                    request, "You have already requested leave for these dates."
                )
                return redirect("teacherDashboard")

            # Create leave request
            leave = StaffLeave.objects.create(
                staff=staff,
                start_date=start_date.date(),
                end_date=end_date.date(),
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

            # Get the staff object - FIX: Use filter().first() instead of get() to avoid MultipleObjectsReturned error
            teacher = Staff.objects.filter(phone=staff.phone).first()

            if not teacher:
                messages.error(request, "Staff account not found")
                return redirect("teacherDashboard")

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
        teacher = Staff.objects.filter(phone=request.user.phone).first()
        if not teacher:
            return redirect("login")
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
    teacher = Staff.objects.filter(phone=request.user.phone).first()
    if not teacher:
        return JsonResponse({"success": False, "message": "Teacher account not found"})
    subject_id = request.GET.get("subject_id")

    if not subject_id:
        return JsonResponse({"success": False, "message": "Subject ID is required"})

    try:
        routines = Routine.objects.filter(
            teacher=teacher, subject_id=subject_id, is_active=True
        ).values("id", "start_time", "end_time", "period_or_year")

        return JsonResponse({"success": True, "schedule": list(routines)})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
def teacher_update_profile_picture(request):
    """View to handle profile picture update for teachers"""
    if request.method == "POST":
        teacher = Staff.objects.filter(phone=request.user.phone).first()
        if not teacher:
            return redirect("login")
        image = request.FILES.get("image")

        if image:
            try:
                # Update the teacher's profile picture
                teacher.image = image
                teacher.save()
                messages.success(request, "Profile picture updated successfully.")
            except Exception as e:
                messages.error(request, f"Error updating profile picture: {str(e)}")
        else:
            messages.error(request, "No profile picture uploaded.")

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
    routine_id = request.GET.get("routine_id")
    date_str = request.GET.get("date")

    if not routine_id or not date_str:
        return JsonResponse({"error": "Missing required parameters"})

    try:
        teacher = Staff.objects.filter(phone=request.user.phone).first()
        if not teacher:
            return JsonResponse({"error": "Teacher account not found"}, status=404)
        routine = Routine.objects.get(id=routine_id, teacher=teacher)
        date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # Get existing attendance data if any
        attendance_data = {"teacher_attend": False, "class_status": True, "records": {}}

        try:
            # Get attendance record with all related data in one query
            attendance = Attendance.objects.select_related("routine").get(
                routine=routine, date=date
            )

            # Get all attendance records for this attendance in one query
            records = AttendanceRecord.objects.filter(
                attendance=attendance
            ).select_related("student")

            attendance_data = {
                "id": attendance.id,
                "date": attendance.date.strftime("%Y-%m-%d"),
                "teacher_attend": attendance.teacher_attend,
                "class_status": attendance.class_status,
                "records": {
                    str(record.student.id): record.student_attend for record in records
                },
            }
        except Attendance.DoesNotExist:
            # No existing attendance record found - return default values
            pass

        return JsonResponse(attendance_data)

    except Routine.DoesNotExist:
        return JsonResponse({"error": "Invalid routine selected"}, status=404)
    except ValueError:
        return JsonResponse({"error": "Invalid date format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def get_students(request):
    """View to handle AJAX request for getting students list"""
    from django.http import JsonResponse

    routine_id = request.GET.get("routine_id")

    if not routine_id:
        return JsonResponse({"error": "Missing routine_id parameter"}, status=400)

    try:
        teacher = Staff.objects.filter(phone=request.user.phone).first()
        if not teacher:
            return JsonResponse({"error": "Teacher account not found"}, status=404)
        routine = Routine.objects.get(id=routine_id, teacher=teacher)

        # Get only active students for this routine
        students = Student.objects.filter(
            course=routine.subject.course,
            current_period=routine.period_or_year,
            status="Active",  # Only get active students
        ).order_by("name")

        # If no students found, try a more flexible approach but still only active students
        if not students.exists():
            students = Student.objects.filter(
                course=routine.subject.course,
                status="Active",  # Maintain active student filter
            ).order_by("name")

        # Format student data for JSON response
        student_data = [
            {"id": student.id, "name": student.name} for student in students
        ]

        return JsonResponse({"students": student_data})

    except Routine.DoesNotExist:
        return JsonResponse({"error": "Invalid routine selected"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["GET", "POST"])
def manage_subject_files(request):
    """View to manage files for subjects taught by the teacher"""
    logger = logging.getLogger(__name__)

    # First check if the user is authenticated and in the Teacher group
    if not request.user.is_authenticated:
        logger.error("User not authenticated")
        return redirect("login")

    # Try to get the teacher object
    teacher = None
    try:
        if hasattr(request.user, "phone"):
            # If the user model has phone attribute (Staff model)
            teacher = Staff.objects.get(phone=request.user.phone)
        else:
            # If request.user is a different model, try to get Staff by ID
            teacher = Staff.objects.get(id=request.user.id)
    except Staff.DoesNotExist:
        logger.error(f"Teacher not found for user: {request.user}")
        messages.error(
            request, "Staff account not found. Please contact administrator."
        )
        return redirect("dashboard")
    except Exception as e:
        logger.error(f"Error getting teacher: {e}", exc_info=True)
        messages.error(request, f"Error retrieving staff profile: {str(e)}")
        return redirect("dashboard")

    logger.info(f"Teacher found: {teacher.name}")

    # Get all subjects taught by this teacher
    subject_filter = request.GET.get("subject")

    subjects_query = (
        Routine.objects.filter(teacher=teacher, is_active=True)
        .values_list("subject", flat=True)
        .distinct()
    )

    logger.info(f"Found {len(subjects_query)} subject IDs: {list(subjects_query)}")

    # Apply subject filter if provided
    try:
        if subject_filter:
            subjects = Subject.objects.filter(
                id=subject_filter, id__in=subjects_query
            ).order_by("course__name", "period_or_year", "name")

            logger.info(
                f"Filtered by subject ID {subject_filter}, found {subjects.count()} subjects"
            )

            # If no subject found with the provided ID, return a helpful error
            if not subjects.exists():
                logger.warning(f"No subjects found with ID {subject_filter}")
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {
                            "success": False,
                            "message": f"Subject with ID {subject_filter} not found or you don't have permission to access it",
                        },
                        status=404,
                    )
                else:
                    return render(
                        request,
                        "teacher/subject_files.html",
                        {
                            "subjects": [],
                            "teacher": teacher,
                            "selected_subject": None,
                            "error_message": f"Subject with ID {subject_filter} not found or you don't have permission to access it",
                        },
                    )
        else:
            subjects = Subject.objects.filter(id__in=subjects_query).order_by(
                "course__name", "period_or_year", "name"
            )

            logger.info(f"No filter applied, found {subjects.count()} subjects")

            # If no subjects found at all, return a message
            if not subjects.exists():
                logger.warning("No subjects found for this teacher")
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "You are not assigned to any subjects yet",
                        }
                    )
                else:
                    return render(
                        request,
                        "teacher/subject_files.html",
                        {
                            "subjects": [],
                            "teacher": teacher,
                            "selected_subject": None,
                            "error_message": "You are not assigned to any subjects yet",
                        },
                    )
    except Exception as e:
        logger.error(f"Error loading subjects: {e}", exc_info=True)
        # Handle any unexpected errors
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": False, "message": f"Error loading subjects: {str(e)}"},
                status=500,
            )
        else:
            return render(
                request,
                "teacher/subject_files.html",
                {
                    "subjects": [],
                    "teacher": teacher,
                    "selected_subject": None,
                    "error_message": f"Error loading subjects: {str(e)}",
                },
            )

    if request.method == "POST":
        subject_id = request.POST.get("subject_id")
        title = request.POST.get("title")
        description = request.POST.get("description")
        file = request.FILES.get("file")

        logger.info(
            f"Processing file upload - subject_id: {subject_id}, title: {title}"
        )

        if not subject_id or not title or not file:
            logger.warning("Missing required fields for file upload")
            return JsonResponse(
                {"success": False, "message": "Subject, title and file are required"}
            )

        try:
            subject = Subject.objects.get(id=subject_id)

            # Check if subject is taught by this teacher
            if not Routine.objects.filter(
                teacher=teacher, subject=subject, is_active=True
            ).exists():
                logger.warning(
                    f"Teacher {teacher.id} does not have permission for subject {subject_id}"
                )
                return JsonResponse(
                    {
                        "success": False,
                        "message": "You don't have permission to upload files to this subject",
                    }
                )

            # Create new subject file
            subject_file = SubjectFile.objects.create(
                subject=subject,
                title=title,
                description=description,
                file=file,
                uploaded_by=teacher,
            )

            logger.info(f"File uploaded successfully: {subject_file.id}")

            return JsonResponse(
                {
                    "success": True,
                    "message": "File uploaded successfully",
                    "file": {
                        "id": subject_file.id,
                        "title": subject_file.title,
                        "description": subject_file.description,
                        "file_url": subject_file.file.url,
                        "uploaded_at": subject_file.uploaded_at.strftime(
                            "%b %d, %Y %H:%M"
                        ),
                    },
                }
            )
        except Subject.DoesNotExist:
            logger.error(f"Subject {subject_id} not found")
            return JsonResponse({"success": False, "message": "Subject not found"})
        except Exception as e:
            logger.error(f"Error uploading file: {e}", exc_info=True)
            return JsonResponse(
                {"success": False, "message": f"Error uploading file: {str(e)}"}
            )

    # For GET requests, return a list of subjects and their files
    subjects_data = []
    for subject in subjects:
        try:
            logger.info(f"Processing subject: {subject.id} - {subject.name}")

            # Manually get the files instead of relying on get_all_files method
            files = []

            # Add syllabus if it exists
            if subject.syllabus_pdf:
                try:
                    files.append(
                        {
                            "id": "syllabus",
                            "title": f"{subject.name} Syllabus",
                            "description": f"Syllabus PDF for {subject.name}",
                            "file_url": subject.syllabus_pdf.url,
                            "file_type": "syllabus",
                            "uploaded_by": None,
                            "uploaded_at": None,
                        }
                    )
                except Exception as syllabus_error:
                    logger.error(
                        f"Error adding syllabus for subject {subject.id}: {syllabus_error}",
                        exc_info=True,
                    )

            # Add subject files
            try:
                subject_files = SubjectFile.objects.filter(subject=subject).order_by(
                    "-uploaded_at"
                )
                logger.info(
                    f"Found {subject_files.count()} additional files for subject {subject.id}"
                )

                for file in subject_files:
                    try:
                        files.append(
                            {
                                "id": file.id,
                                "title": file.title,
                                "description": file.description,
                                "file_url": file.file.url,
                                "file_type": "notes",
                                "uploaded_by": file.uploaded_by.name
                                if file.uploaded_by
                                else None,
                                "uploaded_at": file.uploaded_at,
                            }
                        )
                    except Exception as file_error:
                        logger.error(
                            f"Error adding file {file.id} for subject {subject.id}: {file_error}",
                            exc_info=True,
                        )
            except Exception as files_error:
                logger.error(
                    f"Error getting subject files for subject {subject.id}: {files_error}",
                    exc_info=True,
                )

            logger.info(
                f"Successfully processed {len(files)} files for subject {subject.id}"
            )

            subjects_data.append(
                {
                    "id": subject.id,
                    "name": subject.name,
                    "course": subject.course.name,
                    "semester_or_year": subject.period_or_year,
                    "files": files,
                    "files_count": len(files),
                }
            )
        except Exception as e:
            # If there's an error with a specific subject, log it but continue
            logger.error(f"Error processing subject {subject.id}: {e}", exc_info=True)

    logger.info(f"Rendering template with {len(subjects_data)} subjects")

    # Print to console for debugging
    print(f"DEBUG: Teacher = {teacher.name}, Subjects count = {len(subjects_data)}")
    if subjects_data:
        print(f"DEBUG: First subject = {subjects_data[0]['name']}")
    else:
        print("DEBUG: No subjects data to render")

    return render(
        request,
        "teacher/subject_files.html",
        {
            "subjects": subjects_data,
            "teacher": teacher,
            "selected_subject": subject_filter,
        },
    )


@login_required
@require_http_methods(["POST"])
def delete_subject_file(request):
    """View to delete a subject file"""
    teacher = Staff.objects.filter(phone=request.user.phone).first()
    if not teacher:
        return JsonResponse(
            {"success": False, "message": "Staff account not found"}, status=404
        )

    file_id = request.POST.get("file_id")

    if not file_id:
        return JsonResponse({"success": False, "message": "File ID is required"})

    try:
        # Check if the file exists and is owned by this teacher or from their subject
        subject_file = SubjectFile.objects.get(id=file_id)

        # Check if the file is from a subject taught by this teacher
        if (
            not Routine.objects.filter(
                teacher=teacher, subject=subject_file.subject, is_active=True
            ).exists()
            and subject_file.uploaded_by != teacher
        ):
            return JsonResponse(
                {
                    "success": False,
                    "message": "You don't have permission to delete this file",
                }
            )

        # Delete the file
        subject_file.delete()

        return JsonResponse({"success": True, "message": "File deleted successfully"})
    except SubjectFile.DoesNotExist:
        return JsonResponse({"success": False, "message": "File not found"})
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Error deleting file: {str(e)}"}
        )


@login_required
@require_GET
def get_teacher_subjects(request):
    """View to get a list of subjects taught by the teacher"""
    teacher = Staff.objects.filter(phone=request.user.phone).first()
    if not teacher:
        return JsonResponse(
            {"success": False, "message": "Staff account not found"}, status=404
        )

    # Get all subjects taught by the teacher
    subjects_query = Subject.objects.filter(
        routine__teacher=teacher, routine__is_active=True
    ).distinct()

    # Prepare results with additional has_syllabus field
    subjects_data = []
    for subject in subjects_query:
        subjects_data.append(
            {
                "id": subject.id,
                "name": subject.name,
                "course__name": subject.course.name,
                "period_or_year": subject.period_or_year,
                "has_syllabus": bool(subject.syllabus_pdf),
            }
        )

    return JsonResponse({"success": True, "subjects": subjects_data})


@login_required
@require_GET
def view_subject_syllabus(request, subject_id):
    """View to display syllabus PDF for a subject"""
    teacher = Staff.objects.filter(phone=request.user.phone).first()

    if not teacher:
        return JsonResponse(
            {"success": False, "message": "Staff account not found"}, status=404
        )

    try:
        # Check if the subject_id is valid
        if not subject_id or not str(subject_id).isdigit():
            return JsonResponse(
                {"success": False, "message": "Invalid subject ID provided"}, status=400
            )

        subject_id = int(subject_id)

        # First check if the teacher teaches this subject
        if not Routine.objects.filter(
            teacher=teacher, subject_id=subject_id, is_active=True
        ).exists():
            return JsonResponse(
                {
                    "success": False,
                    "message": "You don't have permission to view this subject's syllabus",
                },
                status=403,
            )

        try:
            subject = Subject.objects.filter(id=subject_id).first()
        except Subject.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Subject not found"}, status=404
            )

        if not subject.syllabus_pdf:
            return JsonResponse(
                {"success": False, "message": "No syllabus available for this subject"},
                status=404,
            )

        # Return JSON with the file URL
        return JsonResponse(
            {
                "success": True,
                "file_url": subject.syllabus_pdf.url,
                "file_name": f"{subject.name} Syllabus.pdf",
            }
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Error retrieving syllabus: {str(e)}"},
            status=500,
        )


@login_required
def staffDashboard(request):
    """View to display the staff dashboard with their personal information and progress"""
    staff = Staff.objects.get(phone=request.user.phone)  # Get the Staff object
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    # Clear section states on page load
    if request.method == "GET":
        request.session.pop("active_section", None)
        request.session.pop("active_subsection", None)

    # Get feedback types for institute feedback
    feedback_types = FEEDBACK_TYPE_CHOICES

    # Get institute feedback
    institute_feedback = StaffInstituteFeedback.objects.filter(staff=staff).order_by(
        "-created_at"
    )[:5]

    # Get recent notices
    recent_notices = Notice.objects.all().order_by("-created_at")[:5]

    # Get recent feedback
    recent_feedback = StudentFeedback.objects.filter(teacher=staff).order_by(
        "-created_at"
    )[:5]

    # Get leave requests
    leave_requests = StaffLeave.objects.filter(staff=staff).order_by("-created_at")[:5]

    # Get routines assigned to this teacher
    routines = Routine.objects.filter(teacher=staff, is_active=True).order_by(
        "start_time"
    )

    # Get today's routines
    today_routines = routines.filter(
        start_time__lte=timezone.now().time(), end_time__gte=timezone.now().time()
    )

    # Get attendance records for today's routines
    today_attendance = Attendance.objects.filter(
        routine__in=today_routines, date=today
    ).select_related("routine")

    # Calculate attendance statistics
    total_students = 0
    present_students = 0
    absent_students = 0

    for attendance in today_attendance:
        records = attendance.records.all()
        total_students += records.count()
        present_students += records.filter(student_attend=True).count()
        absent_students += records.filter(student_attend=False).count()

    # Get average rating from student feedback
    avg_rating = (
        StudentFeedback.objects.filter(teacher=staff).aggregate(Avg("rating"))[
            "rating__avg"
        ]
        or 0
    )

    context = {
        "staff": staff,
        "recent_notices": recent_notices,
        "recent_feedback": recent_feedback,
        "institute_feedback": institute_feedback,
        "leave_requests": leave_requests,
        "today_routines": today_routines,
        "today_attendance": today_attendance,
        "total_students": total_students,
        "present_students": present_students,
        "absent_students": absent_students,
        "avg_rating": avg_rating,
        "feedback_types": feedback_types,
        "last_week": last_week,
        "last_month": last_month,
    }

    return render(request, "teacher/dashboard.html", context)
