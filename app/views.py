from app.models import FCMDevice
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from .models import (
    Student, Course, CourseTracking, 
    Student_Leave, Staff_leave, 
    Attendance, AttendanceRecord,
    StudentFeedback, Routine, StudentRoutine,
    Staff
)
from app.admin import custom_admin_site
# Create your views here.


# FireBase
def saveFCMToken(request, token):
    try:
        FCMDevice(token=token).save()
    except:
        pass
    return JsonResponse({})


def showFirebaseJS(request):
    data = """
        importScripts('https://www.gstatic.com/firebasejs/11.0.2/firebase-app-compat.js');
        importScripts('https://www.gstatic.com/firebasejs/11.0.2/firebase-messaging-compat.js');

        firebase.initializeApp({
            apiKey: "AIzaSyAVzOJh5v8_oZg4MoQkq0CzrAbeyHGn4z4",
            authDomain: "institute-management-sys-a2d20.firebaseapp.com",
            projectId: "institute-management-sys-a2d20",
            storageBucket: "institute-management-sys-a2d20.firebasestorage.app",
            messagingSenderId: "777235542100",
            appId: "1:777235542100:web:4d0cb9553918cb3cc23dc1",
            measurementId: "G-4QP9GYV0SJ"
        });

        const messaging = firebase.messaging();

        messaging.onBackgroundMessage((payload) => {

            const notificationTitle = payload.notification.title;
            const notificationOptions = {
                body: payload.notification.body,
                icon: payload.notification.icon
            };

            return self.registration.showNotification(notificationTitle, notificationOptions);
        });
    """
    return HttpResponse(data, content_type="text/javascript")

@login_required
def dashboard(request):
    user = request.user
    user_groups = user.groups.values_list('name', flat=True)
    if 'Student' in user_groups:
        return redirect('studentDashboard')
    elif 'Teacher' in user_groups:
        return redirect('teacherDashboard')
    # Get current date and date ranges
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    # Student Statistics
    total_students = Student.objects.count()
    active_students = Student.objects.filter(status='Active').count()
    completed_students = Student.objects.filter(status='Completed').count()
    on_leave_students = Student.objects.filter(status='Leave').count()

    # Course Statistics
    total_courses = Course.objects.count()
    active_courses = Course.objects.filter(student_trackings__progress_status='In Progress').distinct().count()
    completed_courses = Course.objects.filter(student_trackings__progress_status='Completed').distinct().count()

    # Course Tracking Statistics
    course_trackings = CourseTracking.objects.all()
    in_progress_trackings = course_trackings.filter(progress_status='In Progress')
    completed_trackings = course_trackings.filter(progress_status='Completed')
    dropped_trackings = course_trackings.filter(progress_status='Dropped')

    # Recent Leave Requests
    recent_student_leaves = Student_Leave.objects.filter(
        created_at__gte=last_week
    ).order_by('-created_at')[:5]

    recent_staff_leaves = Staff_leave.objects.filter(
        created_at__gte=last_week
    ).order_by('-created_at')[:5]

    # Attendance Statistics
    today_attendance = Attendance.objects.filter(date=today).count()
    today_present = AttendanceRecord.objects.filter(
        attendance__date=today,
        student_attend=True
    ).count()

    # Recent Feedback
    recent_feedback = StudentFeedback.objects.order_by('-created_at')[:5]

    # Course Progress Overview
    course_progress = []
    for course in Course.objects.all():
        trackings = course.student_trackings.all()
        if trackings.exists():
            avg_progress = trackings.aggregate(avg_progress=Avg('completion_percentage'))['avg_progress']
            course_progress.append({
                'course': course,
                'total_students': trackings.count(),
                'in_progress': trackings.filter(progress_status='In Progress').count(),
                'completed': trackings.filter(progress_status='Completed').count(),
                'average_progress': round(avg_progress, 1) if avg_progress else 0
            })

    # Monthly Statistics
    monthly_stats = {
        'new_students': Student.objects.filter(joining_date__gte=last_month).count(),
        'completed_courses': completed_trackings.filter(actual_end_date__gte=last_month).count(),
        'attendance_rate': round(
            (AttendanceRecord.objects.filter(
                attendance__date__gte=last_month,
                student_attend=True
            ).count() / 
            AttendanceRecord.objects.filter(
                attendance__date__gte=last_month
            ).count() * 100) if AttendanceRecord.objects.filter(
                attendance__date__gte=last_month
            ).exists() else 0,
            1
        )
    }

    context = {
        **custom_admin_site.each_context(request),  # This adds the admin context, including the sidebar.
        # Student Statistics
        'total_students': total_students,
        'active_students': active_students,
        'completed_students': completed_students,
        'on_leave_students': on_leave_students,

        # Course Statistics
        'total_courses': total_courses,
        'active_courses': active_courses,
        'completed_courses': completed_courses,

        # Course Tracking Statistics
        'in_progress_trackings': in_progress_trackings.count(),
        'completed_trackings': completed_trackings.count(),
        'dropped_trackings': dropped_trackings.count(),

        # Leave Requests
        'recent_student_leaves': recent_student_leaves,
        'recent_staff_leaves': recent_staff_leaves,

        # Attendance Statistics
        'today_attendance': today_attendance,
        'today_present': today_present,
        'attendance_rate': round(
            (today_present / today_attendance * 100) if today_attendance > 0 else 0,
            1
        ),

        # Recent Feedback
        'recent_feedback': recent_feedback,

        # Course Progress
        'course_progress': course_progress,

        # Monthly Statistics
        'monthly_stats': monthly_stats,
    }

    return render(request, 'dashboard.html', context)


@login_required
def studentDashboard(request):
    """View to display the student dashboard with their personal information and progress"""
    student = request.user
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    # Course Progress
    course_trackings = CourseTracking.objects.filter(student=student)
    total_courses = course_trackings.count()
    completed_courses = course_trackings.filter(progress_status='Completed').count()
    in_progress_courses = course_trackings.filter(progress_status='In Progress').count()
    completion_percentage = (completed_courses / total_courses * 100) if total_courses > 0 else 0

    # Course Details
    course_details = {}
    for tracking in course_trackings:
        course_details[tracking.course.name] = {
            'start_date': tracking.start_date,
            'end_date': tracking.end_date,
            'completion_percentage': tracking.completion_percentage,
            'progress_status': tracking.progress_status,
            'book': tracking.course.book if hasattr(tracking.course, 'book') else None,
            'topics': []  # This will be populated if you have topic tracking
        }

    # Attendance Statistics
    attendance_records = AttendanceRecord.objects.filter(student=student)
    total_classes = attendance_records.count()
    classes_attended = attendance_records.filter(student_attend=True).count()
    attendance_percentage = (classes_attended / total_classes * 100) if total_classes > 0 else 0

    # Calculate attendance streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    
    for record in attendance_records.order_by('-attendance__date'):
        if record.student_attend:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
            if record.attendance.date >= last_week:
                current_streak = temp_streak
        else:
            temp_streak = 0

    # Recent Leave Requests
    recent_leaves = Student_Leave.objects.filter(
        student=student
    ).order_by('-created_at')[:5]

    # Recent Feedback
    recent_feedback = StudentFeedback.objects.filter(
        student=student
    ).order_by('-created_at')[:5]

    context = {
        **custom_admin_site.each_context(request),  # This adds the admin context, including the sidebar.
        'student': student,
        'title': 'Student Dashboard',
        
        # Course Summary
        'course_summary': {
            'total_courses': total_courses,
            'completed_courses': completed_courses,
            'ongoing_courses': in_progress_courses,
            'completion_percentage': completion_percentage,
            'details': course_details
        },

        # Attendance Summary
        'attendance_summary': {
            'total_classes': total_classes,
            'classes_attended': classes_attended,
            'attendance_percentage': attendance_percentage,
            'current_streak': current_streak,
            'longest_streak': longest_streak
        },

        # Recent Activity
        'recent_leaves': recent_leaves,
        'recent_feedback': recent_feedback,
    }

    return render(request, 'student_dashboard.html', context)

@login_required
def teacherDashboard(request):
    """View to display the teacher dashboard with their classes and student information"""
    teacher = Staff.objects.get(phone=request.user.phone)  # Get the Staff object
    today = timezone.now().date()
    current_time = timezone.now().time()

    # Get today's routines through attendance
    today_routines = Routine.objects.filter(
        teacher=teacher,
        attendances__date=today
    ).order_by('start_time')

    # Process routines to include status and attendance
    processed_routines = []
    for routine in today_routines:
        attendance = routine.attendances.filter(date=today).first()
        
        total_students = StudentRoutine.objects.filter(routine=routine).count()
        attendance_count = 0 if not attendance else AttendanceRecord.objects.filter(
            attendance=attendance,
            student_attend=True
        ).count()

        processed_routines.append({
            'name': routine.name,
            'start_time': routine.start_time,
            'end_time': routine.end_time,
            'is_completed': routine.end_time < current_time,
            'is_ongoing': routine.start_time <= current_time <= routine.end_time,
            'total_students': total_students,
            'attendance_count': attendance_count
        })

    # Calculate class statistics
    total_classes = today_routines.count()
    completed_classes = len([r for r in processed_routines if r['is_completed']])

    # Get student statistics
    total_students = StudentRoutine.objects.filter(
        routine__teacher=teacher
    ).values('student').distinct().count()

    # Calculate present students for today
    present_students = AttendanceRecord.objects.filter(
        attendance__routine__teacher=teacher,
        attendance__date=today,
        student_attend=True
    ).count()

    # Get teacher's feedback statistics
    feedback = StudentFeedback.objects.filter(teacher=teacher)
    avg_rating = feedback.aggregate(Avg('rating'))['rating__avg'] or 0
    avg_rating_rounded = int(avg_rating)
    remaining_stars = 5 - avg_rating_rounded

    # Get leave statistics
    leaves = Staff_leave.objects.filter(staff=teacher)
    pending_leaves = leaves.filter(status=0).count()
    approved_leaves = leaves.filter(status=1).count()
    rejected_leaves = leaves.filter(status=2).count()

    # Get recent activity
    recent_leaves = leaves.order_by('-created_at')[:5]
    recent_feedback = feedback.order_by('-created_at')[:5]

    context = {
        **custom_admin_site.each_context(request),  # This adds the admin context, including the sidebar.
        'teacher': teacher,
        'title': 'Teacher Dashboard',

        # Class Statistics
        'today_classes': total_classes,
        'completed_classes': completed_classes,
        'today_routines': processed_routines,

        # Student Statistics
        'total_students': total_students,
        'present_students': present_students,

        # Feedback Statistics
        'avg_rating': avg_rating,
        'avg_rating_rounded': avg_rating_rounded,
        'remaining_stars': remaining_stars,

        # Leave Statistics
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'rejected_leaves': rejected_leaves,

        # Recent Activity
        'recent_leaves': recent_leaves,
        'recent_feedback': recent_feedback,
    }

    return render(request, 'teacher_dashboard.html', context)
