# Standard library imports
import random
from datetime import date, timedelta

# Core Django imports
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission
from django.core.cache import cache
from django.core.signals import request_started
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import m2m_changed, post_migrate, post_save, post_delete, pre_save
from django.dispatch import receiver
import logging
from django.utils import timezone

# Local app imports
from app.firebase import FCMDevice, send_push_notification
from app.models import (
    Batch,
    CourseTracking,
    Notice,
    Parent,
    Staff,
    Student,
    TeacherParentMeeting,
    Course,
    Subject,
    TOTPSecret,
    ResetToken,
    OTPAttempt,
    AttendanceRecord,
    StudentLeave,
    Attendance,
    ParentFeedback,
    ParentInstituteFeedback,
    Routine,
    SubjectFile,
)
from app.utils import cleanup_expired_tokens

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------
# Course Tracking Signals
# --------------------------------------------------------------------


@receiver(post_save, sender=CourseTracking)
def update_completion_percentage(sender, instance, **kwargs):
    """
    Signal to update completion percentage after save
    Also caches the percentage for 1 hour to avoid frequent recalculations
    """
    cache_key = f"course_tracking_percentage_{instance.id}"
    cache.set(cache_key, instance.completion_percentage, 3600)  # Cache for 1 hour


@receiver(request_started)
def periodic_update_course_completion(sender, **kwargs):
    """
    Signal that updates course completion percentages randomly on request start.
    This ensures periodic updates without overwhelming the system.
    Only runs with 1% probability per request to avoid performance impact.
    """
    # Run this signal with 1% probability to avoid running on every request
    if random.random() <= 0.01:  # 1% chance to run on any request
        # Get all active course trackings (not completed or dropped)
        active_trackings = CourseTracking.objects.filter(
            Q(progress_status="In Progress") | Q(progress_status="Not Started")
        )

        updated_count = 0
        for tracking in active_trackings:
            old_percentage = tracking.completion_percentage
            new_percentage = tracking.update_completion_percentage()

            # If percentage changed, it was updated
            if old_percentage != new_percentage:
                updated_count += 1

            # Check if course is now complete (100%)
            if new_percentage >= 100 and tracking.progress_status != "Completed":
                tracking.progress_status = "Completed"
                tracking.actual_end_date = date.today()
                tracking.save()

        # Cache the last update timestamp
        if updated_count > 0:
            cache.set(
                "last_course_percentage_update", date.today().isoformat(), 86400
            )  # 24 hours


# --------------------------------------------------------------------
# Student and Course Signals
# --------------------------------------------------------------------


@receiver(post_save, sender=Student)
def create_course_tracking(sender, instance, created, **kwargs):
    """
    Signal handler to create CourseTracking when a new student is created
    or when a course is assigned to an existing student
    """
    # Skip if signal is triggered due to our own update
    if getattr(instance, '_skip_course_tracking_signal', False):
        return
    
    # Check if student has a course assigned
    if not instance.course:
        return
    
    # Check if course tracking already exists (outside of any transaction)
    existing_tracking = CourseTracking.objects.filter(
        student=instance, course=instance.course
    ).first()
    
    if existing_tracking:
        return  # Skip if already exists
        
    try:
        # Calculate dates based on course duration
        start_date = instance.joining_date or date.today()

        # Calculate expected end date based on course duration type
        years = instance.course.duration
        duration_days = years * 365  # Use full years for total duration
        expected_end_date = start_date + timedelta(days=duration_days)
        
        # Set period dates based on duration type
        period_start_date = start_date
        if instance.course.duration_type == "Semester":
            period_end_date = start_date + timedelta(days=180)  # 6 months
        else:
            period_end_date = start_date + timedelta(days=365)  # 1 year
        
        # Create a new CourseTracking instance
        CourseTracking.objects.create(
            student=instance,
            course=instance.course,
            start_date=start_date,
            expected_end_date=expected_end_date,
            current_period=instance.current_period,
            period_start_date=period_start_date,
            period_end_date=period_end_date,
            progress_status="In Progress"
        )
        
        # Log success but don't trigger any more signals
        logger.info(f"Created course tracking for student: {instance.name}")
    
    except Exception as e:
        # Log the error properly
        error_msg = f"Error creating course tracking for student {instance.name}: {str(e)}"
        logger.error(error_msg)
        # Do not raise the exception - let the student save proceed


@receiver(post_save, sender=Student)
def sync_student_period(sender, instance, created, **kwargs):
    """Signal handler to sync student's current_period with course tracking"""
    if instance.course:
        try:
            course_tracking = CourseTracking.objects.get(
                student=instance, course=instance.course
            )
            if course_tracking.current_period != instance.current_period:
                course_tracking.current_period = instance.current_period
                course_tracking.save()
        except CourseTracking.DoesNotExist:
            pass


@receiver(post_save, sender=CourseTracking)
def sync_course_tracking_period(sender, instance, created, **kwargs):
    """Signal handler to sync course tracking's current_period with student"""
    if instance.student.current_period != instance.current_period:
        instance.student.current_period = instance.current_period
        instance.student.save()


# --------------------------------------------------------------------
# Parent and Student Relationship Signals
# --------------------------------------------------------------------


@receiver(post_save, sender=Student)
def create_parent_for_student(sender, instance, created, **kwargs):
    """
    Signal to create or update parent when a student is created or updated.
    Also ensures parent is assigned to the Parent group.
    """
    if instance.parent_name and instance.parent_phone:
        try:
            # Try to find existing parent
            parent = Parent.objects.filter(phone=instance.parent_phone).first()

            if not parent:
                # Create new parent if doesn't exist
                parent = Parent.objects.create(
                    name=instance.parent_name,
                    phone=instance.parent_phone,
                    password=make_password("123"),  # Default password
                )

                # Get or create Parent group
                parent_group, _ = Group.objects.get_or_create(name="Parent")

                # Add parent to group
                parent.groups.add(parent_group)

                # Add necessary permissions
                permissions = Permission.objects.filter(
                    codename__in=["view_student", "view_attendance", "view_notice"]
                )
                parent_group.permissions.add(*permissions)

            # Add student to parent's students
            parent.students.add(instance)

        except Exception as e:
            print(f"Error creating/updating parent: {str(e)}")
            # Don't prevent student creation/update if parent creation fails


@receiver(post_save, sender=Parent)
def setup_parent_user(sender, instance, created, **kwargs):
    """
    Signal handler to set up a new parent user:
    1. Add to Parent group
    2. Set up initial settings and permissions
    """
    if created:
        try:
            # Add user to Parent group
            parent_group, _ = Group.objects.get_or_create(name="Parent")
            instance.groups.add(parent_group)

            print(f"Successfully set up new parent user: {instance.name}")

        except Exception as e:
            print(f"Error setting up parent user {instance.name}: {str(e)}")


@receiver(m2m_changed, sender=Parent.students.through)
def handle_parent_student_relationship(
    sender, instance, action, reverse, model, pk_set, **kwargs
):
    """
    Signal handler to manage parent-student relationship changes:
    - Update caches
    - Handle notifications
    - Sync permissions
    """
    if action == "post_add":
        try:
            if reverse:
                # This is triggered when students are added to a parent
                parent = model.objects.get(pk=pk_set.pop())
                student = instance
            else:
                # This is triggered when a parent adds students
                parent = instance
                student_ids = pk_set

            # Clear parent dashboard cache using a more compatible approach
            cache.delete(f"parent_dashboard_{parent.id}")

            print(
                f"Successfully updated parent-student relationship for parent: {parent.name}"
            )

        except Exception as e:
            print(f"Error handling parent-student relationship: {str(e)}")


# --------------------------------------------------------------------
# User Group and Permission Signals
# --------------------------------------------------------------------


@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    """
    Signal handler to create default user groups after database migrations:
    - Student
    - Parent
    - Teacher
    - HOD
    - Admission Officer
    """
    if sender.name == 'app':  # Only run for our app's migrations
        try:
            # Create Student group
            student_group, created = Group.objects.get_or_create(name="Student")
            if created:
                # Add basic student permissions
                permissions = Permission.objects.filter(
                    codename__in=[
                        "view_routine", 
                        "view_attendance", 
                        "view_notice",
                        "add_studentleave",
                        "view_studentleave"
                    ]
                )
                student_group.permissions.add(*permissions)
                logger.info("Created Student group with basic permissions")
            
            # Create Parent group
            parent_group, created = Group.objects.get_or_create(name="Parent")
            if created:
                # Add basic parent permissions
                permissions = Permission.objects.filter(
                    codename__in=[
                        "view_student", 
                        "view_attendance", 
                        "view_notice",
                        "view_routine"
                    ]
                )
                parent_group.permissions.add(*permissions)
                logger.info("Created Parent group with basic permissions")
            
            # Create Teacher group
            teacher_group, created = Group.objects.get_or_create(name="Teacher")
            if created:
                # Add teacher permissions
                permissions = Permission.objects.filter(
                    codename__in=[
                        "view_student", 
                        "view_attendance", 
                        "add_attendance",
                        "change_attendance",
                        "view_notice",
                        "view_routine",
                        "view_subject"
                    ]
                )
                teacher_group.permissions.add(*permissions)
                logger.info("Created Teacher group with basic permissions")
                
            # Create HOD group
            hod_group, created = Group.objects.get_or_create(name="HOD")
            if created:
                # Add HOD permissions - more permissions than regular teacher
                permissions = Permission.objects.filter(
                    codename__in=[
                        "view_student", 
                        "add_student",
                        "change_student",
                        "view_attendance", 
                        "add_attendance",
                        "change_attendance",
                        "view_notice",
                        "add_notice",
                        "change_notice",
                        "view_routine",
                        "add_routine",
                        "change_routine",
                        "view_subject",
                        "add_subject",
                        "change_subject",
                        "view_staff",
                        "view_course"
                    ]
                )
                hod_group.permissions.add(*permissions)
                logger.info("Created HOD group with administrative permissions")
                
            # Create Admission Officer group
            admission_group, created = Group.objects.get_or_create(name="Admission Officer")
            if created:
                # Add admission officer permissions
                permissions = Permission.objects.filter(
                    codename__in=[
                        "view_student", 
                        "add_student",
                        "change_student",
                        "view_course",
                        "view_batch",
                        "add_batch",
                        "change_batch"
                    ]
                )
                admission_group.permissions.add(*permissions)
                logger.info("Created Admission Officer group with admission permissions")
                
        except Exception as e:
            logger.error(f"Error creating default user groups: {str(e)}")


# --------------------------------------------------------------------
# Batch and Student Enrollment Signals
# --------------------------------------------------------------------


@receiver(post_save, sender=Batch)
def update_student_joining_dates(sender, instance, **kwargs):
    """Update joining dates for all students in a batch when batch year changes"""
    if instance.year:
        # Update all students in this batch who don't have a joining date
        for student in instance.students.filter(joining_date__isnull=True):
            student.joining_date = instance.year
            student.save(update_fields=["joining_date"])


@receiver(m2m_changed, sender=Student.batches.through)
def handle_student_batch_change(
    sender, instance, action, reverse, model, pk_set, **kwargs
):
    """Handle joining date when a student is added to a batch"""
    if action == "post_add" and not reverse:
        # This is fired when batches are added to a student
        for batch_id in pk_set:
            try:
                batch = Batch.objects.get(pk=batch_id)
                if batch.year and not instance.joining_date:
                    instance.joining_date = batch.year
                    instance.save(update_fields=["joining_date"])
                break  # Use the first batch with a joining date
            except Batch.DoesNotExist:
                pass


# --------------------------------------------------------------------
# Notification Signals
# --------------------------------------------------------------------


@receiver(post_save, sender=Notice)
def send_notice_notification(sender, instance, created, **kwargs):
    """
    Send notification when a notice is created or updated
    """
    try:
        if created:
            title = "New Notice"
            message = instance.message
        else:
            title = "Notice Updated"
            message = instance.message
            
        # Get all active FCM tokens
        tokens = list(instance.get_notification_tokens())
        
        if tokens:
            send_push_notification(title, message, tokens)
            logger.info(f"Sent notice notification to {len(tokens)} devices")
    except Exception as e:
        logger.error(f"Error sending notice notification: {str(e)}")


@receiver(post_save, sender=TeacherParentMeeting)
def send_meeting_notification(sender, instance, created, **kwargs):
    """
    Send notification when a meeting is created or updated
    """
    try:
        if created:
            title = "New Parent-Teacher Meeting"
            message = f"Meeting scheduled for {instance.meeting_date} at {instance.meeting_time}"
        else:
            title = "Meeting Updated"
            message = f"Meeting details updated for {instance.meeting_date}"
            
        # Get all active FCM tokens
        tokens = list(instance.get_notification_tokens())
        
        if tokens:
            send_push_notification(title, message, tokens)
            logger.info(f"Sent meeting notification to {len(tokens)} devices")
    except Exception as e:
        logger.error(f"Error sending meeting notification: {str(e)}")


# --------------------------------------------------------------------
# Data Cleanup Signals
# --------------------------------------------------------------------

@receiver(post_delete, sender=Student)
def cleanup_orphaned_student_data(sender, instance, **kwargs):
    """
    Clean up orphaned data when a student is deleted
    """
    try:
        # Handle cleanup safely without relying on the model's method
        # Delete attendance records
        AttendanceRecord.objects.filter(student=instance).delete()
        
        # Delete course tracking
        CourseTracking.objects.filter(student=instance).delete()
        
        # Delete leave requests
        StudentLeave.objects.filter(student=instance).delete()
        
        # Clear any cached data
        cache.delete(f"student_{instance.id}_profile")
        cache.delete(f"student_{instance.id}_progress")
        cache.delete(f"student_{instance.id}_attendance")
        
        logger.info(f"Cleaned up orphaned data for deleted student: {instance.id}")
    except Exception as e:
        logger.error(f"Error cleaning up orphaned student data: {str(e)}")

@receiver(post_delete, sender=Staff)
def cleanup_orphaned_staff_data(sender, instance, **kwargs):
    """
    Clean up orphaned data when a staff member is deleted
    """
    try:
        # Handle cleanup safely without relying on the model's method
        # Delete attendance records where this staff is the teacher
        Attendance.objects.filter(teacher=instance).delete()
        
        # Clear course relationships
        instance.courses_taught.clear()
        
        # Clear any cached data
        cache.delete(f"staff_{instance.id}_profile")
        cache.delete(f"staff_{instance.id}_schedule")
        
        logger.info(f"Cleaned up orphaned data for deleted staff: {instance.id}")
    except Exception as e:
        logger.error(f"Error cleaning up orphaned staff data: {str(e)}")

@receiver(post_delete, sender=CourseTracking)
def cleanup_orphaned_course_tracking_data(sender, instance, **kwargs):
    """
    Clean up orphaned data when a course tracking record is deleted
    """
    try:
        # No need for transaction, just clear cache
        # CourseTracking doesn't have its own cleanup_orphaned_data method
        
        # Clear any cached data - use individual deletions instead of patterns
        cache.delete(f"course_tracking_{instance.id}_percentage")
        if instance.student:
            cache.delete(f"student_{instance.student.id}_progress")
        
        logger.info(f"Cleaned up cached data for deleted course tracking: {instance.id}")
    except Exception as e:
        logger.error(f"Error cleaning up orphaned course tracking data: {str(e)}")

@receiver(post_delete, sender=Parent)
def cleanup_orphaned_parent_data(sender, instance, **kwargs):
    """
    Clean up orphaned data when a parent is deleted
    """
    try:
        # Handle cleanup safely without relying on the model's method
        # Delete feedback records
        ParentFeedback.objects.filter(parent=instance).delete()
        
        # Delete institute feedback
        ParentInstituteFeedback.objects.filter(parent=instance).delete()
        
        # Clear any cached data
        cache.delete(f"parent_{instance.id}_profile")
        cache.delete(f"parent_{instance.id}_students")
        
        logger.info(f"Cleaned up orphaned data for deleted parent: {instance.id}")
    except Exception as e:
        logger.error(f"Error cleaning up orphaned parent data: {str(e)}")

@receiver(post_delete, sender=Course)
def cleanup_orphaned_course_data(sender, instance, **kwargs):
    """
    Clean up orphaned data when a course is deleted
    """
    try:
        # Handle cleanup safely without relying on the model's method
        # Delete subjects
        Subject.objects.filter(course=instance).delete()
        
        # Delete course tracking records
        CourseTracking.objects.filter(course=instance).delete()
        
        # Delete routines
        Routine.objects.filter(course=instance).delete()
        
        # Clear any cached data
        cache.delete(f"course_{instance.id}_details")
        cache.delete(f"course_{instance.id}_subjects")
        
        logger.info(f"Cleaned up orphaned data for deleted course: {instance.id}")
    except Exception as e:
        logger.error(f"Error cleaning up orphaned course data: {str(e)}")

@receiver(post_delete, sender=Subject)
def cleanup_orphaned_subject_data(sender, instance, **kwargs):
    """
    Clean up orphaned data when a subject is deleted
    """
    try:
        # Handle cleanup safely without relying on the model's method
        # Delete subject files
        SubjectFile.objects.filter(subject=instance).delete()
        
        # Delete routines
        Routine.objects.filter(subject=instance).delete()
        
        # Delete attendance records
        attendances = Attendance.objects.filter(routine__subject=instance)
        for attendance in attendances:
            attendance.delete()
        
        # Clear any cached data
        cache.delete(f"subject_{instance.id}_details")
        cache.delete(f"subject_{instance.id}_files")
        
        logger.info(f"Cleaned up orphaned data for deleted subject: {instance.id}")
    except Exception as e:
        logger.error(f"Error cleaning up orphaned subject data: {str(e)}")

# --------------------------------------------------------------------
# Data Validation Signals
# --------------------------------------------------------------------

@receiver(pre_save, sender=Student)
def validate_student_data(sender, instance, **kwargs):
    """
    Validate student data before saving
    """
    try:
        instance.validate_data()
        logger.info(f"Validated student data for: {instance.id}")
    except Exception as e:
        logger.error(f"Error validating student data: {str(e)}")
        raise

@receiver(pre_save, sender=Staff)
def validate_staff_data(sender, instance, **kwargs):
    """
    Validate staff data before saving
    """
    try:
        instance.validate_data()
        logger.info(f"Validated staff data for: {instance.id}")
    except Exception as e:
        logger.error(f"Error validating staff data: {str(e)}")
        raise

# --------------------------------------------------------------------
# Course Progress Signals
# --------------------------------------------------------------------

@receiver(post_save, sender=CourseTracking)
def update_course_progress(sender, instance, **kwargs):
    """
    Update course progress when tracking data changes
    """
    try:
        # Update completion percentage
        instance.update_completion_percentage()
        
        # Update progress status
        if instance.completion_percentage >= 100:
            instance.progress_status = "Completed"
            instance.actual_end_date = date.today()
            instance.save()
        
        # Clear cache using individual keys instead of pattern
        cache.delete(f"course_tracking_{instance.id}_percentage")
        cache.delete(f"student_{instance.student.id}_progress")
        
        logger.info(f"Updated course progress for tracking: {instance.id}")
    except Exception as e:
        logger.error(f"Error updating course progress: {str(e)}")

@receiver(post_save, sender=TOTPSecret)
@receiver(post_save, sender=ResetToken)
def cleanup_expired_tokens_signal(sender, instance, **kwargs):
    """
    Signal handler to clean up expired tokens when a new token is created
    """
    try:
        # Clean up expired OTP secrets and reset tokens
        cleanup_expired_tokens()
        
        # Reset OTP attempts for expired lockouts
        expired_lockouts = OTPAttempt.objects.filter(
            is_locked=True,
            lock_until__lt=timezone.now()
        )
        expired_count = expired_lockouts.count()
        expired_lockouts.update(
            is_locked=False,
            lock_until=None,
            attempts=0
        )
        
        # Log cleanup results to terminal
        print(f'[OTP Cleanup] Successfully cleaned up expired tokens and reset {expired_count} expired lockouts')
        logger.info(f'Successfully cleaned up expired tokens and reset {expired_count} expired lockouts')
    except Exception as e:
        error_msg = f"Error in cleanup signal: {str(e)}"
        print(f'[OTP Cleanup Error] {error_msg}')
        logger.error(error_msg)
        raise

@receiver(post_delete, sender=TOTPSecret)
@receiver(post_delete, sender=ResetToken)
def cleanup_after_deletion(sender, instance, **kwargs):
    """
    Signal handler to clean up expired tokens when a token is deleted
    """
    try:
        cleanup_expired_tokens()
        print('[OTP Cleanup] Successfully cleaned up expired tokens after deletion')
        logger.info('Successfully cleaned up expired tokens after deletion')
    except Exception as e:
        error_msg = f"Error in cleanup after deletion: {str(e)}"
        print(f'[OTP Cleanup Error] {error_msg}')
        logger.error(error_msg)
        raise

# Add a new signal for terminal OTP verification
@receiver(post_save, sender=OTPAttempt)
def handle_terminal_otp_attempt(sender, instance, created, **kwargs):
    """
    Signal handler for terminal-based OTP attempts
    """
    if created:
        try:
            # Get the identifier (phone/email) for logging
            identifier = instance.identifier
            username = instance.user.username if instance.user else identifier
            
            # Log the OTP attempt to terminal
            print(f'[OTP Attempt] User: {username}, Attempts: {instance.attempts}')
            
            # Check if user is locked out
            if instance.is_locked:
                print(f'[OTP Lockout] User {username} is locked until {instance.lock_until}')
            
            # Log to file as well
            logger.info(f'OTP attempt for user {username}, attempts: {instance.attempts}')
        except Exception as e:
            error_msg = f"Error handling OTP attempt: {str(e)}"
            print(f'[OTP Error] {error_msg}')
            logger.error(error_msg)
            raise
