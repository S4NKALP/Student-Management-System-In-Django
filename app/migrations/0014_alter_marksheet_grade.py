# Generated by Django 5.1.4 on 2025-01-08 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_alter_marksheet_grade_alter_marksheet_obtained_marks_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marksheet',
            name='grade',
            field=models.CharField(blank=True, choices=[('A+', 'Excellent'), ('A', 'Very Good'), ('B+', 'Good'), ('B', 'G'), ('C+', 'Average'), ('C', 'A'), ('D+', 'Below Average'), ('D', 'Fail')], help_text='Grade assigned based on marks', max_length=2, null=True),
        ),
    ]