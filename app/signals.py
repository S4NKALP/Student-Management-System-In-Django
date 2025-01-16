from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from app.models import Student, Teacher, Staff


@receiver(post_save, sender=Student)
def assign_student_group(sender, instance, created, **kwargs):
    if created:
        # Ensure the group exists
        student_group, created = Group.objects.get_or_create(name="student")
        instance.user.groups.add(student_group)
        instance.user.save()


@receiver(post_save, sender=Teacher)
def assign_teacher_group(sender, instance, created, **kwargs):
    if created:
        # Ensure the group exists
        teacher_group, created = Group.objects.get_or_create(name="teacher")
        instance.user.groups.add(teacher_group)
        instance.user.save()


@receiver(post_save, sender=Staff)
def assign_staff_group(sender, instance, created, **kwargs):
    if created:
        # Ensure the group exists
        staff_group, created = Group.objects.get_or_create(name="staff")
        instance.user.groups.add(staff_group)
        instance.user.save()
