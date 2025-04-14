from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect

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
)


@login_required
def hod_dashboard(request):
    """HOD dashboard view showing department overview and management options"""
    try:
        # Check if user is a HOD
        if not request.user.groups.filter(name="HOD").exists():
            messages.error(request, "Only HODs can access this dashboard.")
            return redirect("login")

        # Get the HOD's department (course)
        hod = request.user
        if not hasattr(hod, "course") or not hod.course:
            messages.error(request, "You are not assigned as HOD of any department.")
            return redirect("login")

        course = hod.course

        # Get department statistics
        total_students = Student.objects.filter(course=course).count()
        total_staff = Staff.objects.filter(course=course).count()
        total_subjects = Subject.objects.filter(course=course).count()

        # Get subjects for the course
        subjects = Subject.objects.filter(course=course).select_related("course")

        # Get routines to find teachers for each subject
        routines = Routine.objects.filter(course=course, is_active=True).select_related(
            "subject", "teacher"
        )

        # Create a mapping of subject_id to teacher
        teacher_map = {}
        for routine in routines:
            teacher_map[routine.subject_id] = routine.teacher

        # Count students for each subject and attach teacher info
        for subject in subjects:
            # Attach teacher if available from routines
            subject.teacher = teacher_map.get(subject.id)

            # Count students in this subject's period
            subject.student_count = Student.objects.filter(
                course=course, current_period=subject.period_or_year
            ).count()

        # Get subject distribution data for chart - count subjects by period
        subject_distribution = []
        max_periods = (
            8 if course.duration_type == "Semester" else 4
        )  # Max 8 semesters or 4 years
        for i in range(1, max_periods + 1):
            if i <= (
                course.duration * 2
                if course.duration_type == "Semester"
                else course.duration
            ):
                period_count = subjects.filter(period_or_year=i).count()
                subject_distribution.append(period_count)

        # Get today's classes and their attendance
        today = timezone.now().date()
        today_classes = Routine.objects.filter(
            course=course, is_active=True
        ).select_related("subject", "teacher")

        # Get attendance for today's classes
        today_attendance = Attendance.objects.filter(
            routine__course=course, date=today
        ).select_related("routine")

        # Create a dictionary of routine_id to attendance
        attendance_map = {att.routine_id: att for att in today_attendance}

        # Attach attendance to each class
        for class_obj in today_classes:
            class_obj.attendance = attendance_map.get(class_obj.id)

        # Get student progress
        student_progress = (
            CourseTracking.objects.filter(student__course=course)
            .select_related("student")
            .order_by("-completion_percentage")[:5]
        )

        # Get upcoming meetings
        upcoming_meetings = TeacherParentMeeting.objects.filter(
            meeting_date__gte=today, status="scheduled"
        ).order_by("meeting_date", "meeting_time")[:5]

        # Get recent feedback
        recent_feedback = (
            StudentFeedback.objects.filter(student__course=course)
            .select_related("student", "teacher")
            .order_by("-created_at")[:5]
        )

        context = {
            "title": "HOD Dashboard",
            "hod": hod,
            "course": course,
            "total_students": total_students,
            "total_staff": total_staff,
            "total_subjects": total_subjects,
            "today_classes": today_classes,
            "student_progress": student_progress,
            "upcoming_meetings": upcoming_meetings,
            "recent_feedback": recent_feedback,
            "subjects": subjects,
            "subject_distribution": subject_distribution,
        }

        return render(request, "hod/dashboard.html", context)

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("login")
