from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from datetime import date, timedelta
from .models import CourseTracking, Student
from django.db import transaction

@receiver(post_save, sender=CourseTracking)
def update_completion_percentage(sender, instance, **kwargs):
    """
    Signal to update completion percentage after save
    Also caches the percentage for 1 hour to avoid frequent recalculations
    """
    cache_key = f"course_tracking_percentage_{instance.id}"
    cache.set(cache_key, instance.completion_percentage, 3600)  # Cache for 1 hour


@receiver(post_save, sender=Student)
def create_course_tracking(sender, instance, created, **kwargs):
    """
    Signal handler to create CourseTracking when a new student is created
    or when a course is assigned to an existing student
    """
    print(f"Signal triggered for student: {instance.name}")
    print(f"Created: {created}")
    print(f"Course: {instance.course}")
    print(f"Current Semester: {instance.current_semester}")

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
                    current_semester=instance.current_semester,
                    semester_start_date=start_date,
                    semester_end_date=start_date
                    + timedelta(days=180),  # 6 months for first semester
                )

                # Force initial percentage calculation
                course_tracking.force_update_percentage()

                print(
                    f"Successfully created course tracking for student {instance.name}"
                )
                print(f"Start Date: {start_date}")
                print(f"Expected End Date: {expected_end_date}")
                print(f"Current Semester: {instance.current_semester}")

        except Exception as e:
            print(
                f"Error creating course tracking for student {instance.name}: {str(e)}"
            )
            # Log the error but don't prevent student creation
            # You might want to add proper logging here instead of print statements
    else:
        print(f"No course assigned to student {instance.name}")


@receiver(post_save, sender=Student)
def sync_student_semester(sender, instance, created, **kwargs):
    """Signal handler to sync student's current_semester with course tracking"""
    if instance.course:
        try:
            course_tracking = CourseTracking.objects.get(
                student=instance, course=instance.course
            )
            if course_tracking.current_semester != instance.current_semester:
                course_tracking.current_semester = instance.current_semester
                course_tracking.save()
        except CourseTracking.DoesNotExist:
            pass


@receiver(post_save, sender=CourseTracking)
def sync_course_tracking_semester(sender, instance, created, **kwargs):
    """Signal handler to sync course tracking's current_semester with student"""
    if instance.student.current_semester != instance.current_semester:
        instance.student.current_semester = instance.current_semester
        instance.student.save() 