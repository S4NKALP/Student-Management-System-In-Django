# Generated by Django 5.1.5 on 2025-01-16 17:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_remove_subject_description_subject_duration"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="academic_year",
            field=models.ForeignKey(
                default="1",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="students",
                to="app.academicyear",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="student",
            name="course",
            field=models.ForeignKey(
                default="1",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="students",
                to="app.course",
            ),
            preserve_default=False,
        ),
    ]
