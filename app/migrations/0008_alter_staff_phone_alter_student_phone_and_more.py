# Generated by Django 5.1.4 on 2025-01-07 06:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_staff_user_student_user_teacher_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='phone',
            field=models.CharField(max_length=10, validators=[django.core.validators.RegexValidator('^\\+?1?\\d{9,15}$')]),
        ),
        migrations.AlterField(
            model_name='student',
            name='phone',
            field=models.CharField(max_length=10, validators=[django.core.validators.RegexValidator('^\\+?1?\\d{9,15}$')]),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='phone',
            field=models.CharField(max_length=10, validators=[django.core.validators.RegexValidator('^\\+?1?\\d{9,15}$')]),
        ),
    ]