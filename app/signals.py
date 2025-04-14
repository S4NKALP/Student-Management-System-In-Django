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
from django.db.models.signals import m2m_changed, post_migrate, post_save
from django.dispatch import receiver

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
)

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

    # Check if student has a course assigned
    if instance.course:
        try:
            # Check if course tracking already exists
            existing_tracking = CourseTracking.objects.filter(
                student=instance, course=instance.course
            ).first()

            if existing_tracking:
                print(f"Course tracking already exists for {instance.name}")
                return

            # Calculate dates based on course duration
            start_date = instance.joining_date or date.today()

            # Calculate expected end date based on course duration type
            if instance.course.duration_type == "Year":
                # For year-based courses, each year is 365 days
                years = instance.course.duration
                duration_days = years * 365
            else:  # Semester based
                # For semester-based courses:
                # - Each year has 2 semesters
                # - Total years is the same as course duration
                years = instance.course.duration
                duration_days = years * 365  # Use full years for total duration

            expected_end_date = start_date + timedelta(days=duration_days)

            # Create course tracking with transaction
            with transaction.atomic():
                course_tracking = CourseTracking.objects.create(
                    student=instance,
                    course=instance.course,
                    start_date=start_date,
                    expected_end_date=expected_end_date,
                    current_period=instance.current_period,
                    period_start_date=start_date,
                    period_end_date=start_date
                    + timedelta(days=180),  # 6 months for first semester
                )

                # Force initial percentage calculation
                course_tracking.force_update_percentage()

        except Exception as e:
            print(
                f"Error creating course tracking for student {instance.name}: {str(e)}"
            )
            # Log the error but don't prevent student creation
            # You might want to add proper logging here instead of print statements
    else:
        print(f"No course assigned to student {instance.name}")


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
    Create initial user groups and permissions after migrations.
    This ensures groups exist before any user is created.
    """
    from django.contrib.auth.models import Group, Permission

    # Create the necessary groups
    groups_data = {
        "Student": ["view_attendance", "view_notice", "view_subject"],
        "Teacher": [
            "view_student",
            "view_attendance",
            "add_attendance",
            "change_attendance",
            "view_notice",
            "add_notice",
            "view_subject",
            "change_subject",
        ],
        "Parent": ["view_student", "view_attendance", "view_notice"],
        "Admission Officer": [
            "view_student",
            "add_student",
            "change_student",
            "view_parent",
            "add_parent",
            "change_parent",
            "view_course",
            "view_batch",
            "view_notice",
        ],
    }

    for group_name, permissions in groups_data.items():
        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            print(f"Created user group: {group_name}")

            # Add permissions to group
            perms = Permission.objects.filter(codename__in=permissions)
            group.permissions.add(*perms)
            print(f"Added {perms.count()} permissions to {group_name} group")


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
    """Send notifications when a notice is created or updated"""
    # Get all tokens from active devices (all user types)
    tokens = FCMDevice.objects.filter(is_active=True).values_list("token", flat=True)

    send_push_notification(instance.title, instance.message, tokens)


@receiver(post_save, sender=TeacherParentMeeting)
def send_meeting_notification(sender, instance, created, **kwargs):
    """Send notifications when a meeting is created or updated"""
    tokens = []

    # Method 1: Get tokens from FCMDevice records based on user_type
    fcm_device_tokens = FCMDevice.objects.filter(
        is_active=True, user_type__in=["parent", "teacher"]
    ).values_list("token", flat=True)
    tokens.extend(fcm_device_tokens)

    # Method 2: Get tokens directly from user models
    # Get tokens from Staff model
    staff_tokens = (
        Staff.objects.filter(fcm_token__isnull=False)
        .exclude(fcm_token="")
        .values_list("fcm_token", flat=True)
    )
    tokens.extend(staff_tokens)

    # Get tokens from Parent model
    parent_tokens = (
        Parent.objects.filter(fcm_token__isnull=False)
        .exclude(fcm_token="")
        .values_list("fcm_token", flat=True)
    )
    tokens.extend(parent_tokens)

    # Remove duplicates
    unique_tokens = list(set(tokens))

    if not unique_tokens:
        return

    if created:
        title = "New Parent-Teacher Meeting Scheduled"
        message = f"A parent-teacher meeting has been scheduled for {instance.meeting_date} at {instance.meeting_time}."
        if instance.is_online:
            message += " This is an online meeting."
        send_push_notification(title, message, unique_tokens)
    else:
        # Access through instance.tracker to determine if status changed
        # This requires django-model-utils or similar to track changes
        if hasattr(instance, "tracker") and "status" in instance.tracker.changed():
            old_status = instance.tracker.previous("status")
            if instance.status == "cancelled":
                title = "Parent-Teacher Meeting Cancelled"
                message = f"The meeting for {instance.meeting_date} at {instance.meeting_time} has been cancelled."
                if instance.cancellation_reason:
                    message += f" Reason: {instance.cancellation_reason}"
                send_push_notification(title, message, unique_tokens)
            elif instance.status == "rescheduled":
                # Meeting rescheduled notification
                title = "Parent-Teacher Meeting Rescheduled"
                message = f"The parent-teacher meeting has been rescheduled to {instance.meeting_date} at {instance.meeting_time}."
                send_push_notification(title, message, unique_tokens)
            elif instance.status == "completed":
                # Meeting completed notification
                title = "Parent-Teacher Meeting Completed"
                message = f"The parent-teacher meeting scheduled for {instance.meeting_date} at {instance.meeting_time} has been marked as completed."
                send_push_notification(title, message, unique_tokens)
