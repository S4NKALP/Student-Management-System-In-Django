# Generated by Django 5.1.5 on 2025-01-18 10:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0013_student_fcm_token_student_password_student_user_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="student",
            name="user",
        ),
        migrations.RemoveField(
            model_name="student",
            name="username",
        ),
        migrations.RemoveField(
            model_name="teacher",
            name="user",
        ),
        migrations.RemoveField(
            model_name="teacher",
            name="username",
        ),
    ]