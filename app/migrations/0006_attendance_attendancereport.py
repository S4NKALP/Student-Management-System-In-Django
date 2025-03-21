# Generated by Django 5.1.5 on 2025-01-16 17:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_student_academic_year_student_course"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attendance",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("attendance_date", models.DateField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "academic_year",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="app.academicyear",
                    ),
                ),
                (
                    "subject_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING, to="app.subject"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AttendanceReport",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("status", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now_add=True)),
                (
                    "attendance_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="app.attendance"
                    ),
                ),
                (
                    "student_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING, to="app.student"
                    ),
                ),
            ],
        ),
    ]
