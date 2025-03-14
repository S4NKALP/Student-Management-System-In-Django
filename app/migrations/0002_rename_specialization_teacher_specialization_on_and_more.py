# Generated by Django 5.1.5 on 2025-01-16 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="teacher",
            old_name="specialization",
            new_name="specialization_on",
        ),
        migrations.AlterField(
            model_name="teacher",
            name="qualification",
            field=models.CharField(
                choices=[
                    ("SLC", "SLC"),
                    ("Intermediate", "Intermediate"),
                    ("BA", "BA"),
                    ("BBS", "BBS"),
                    ("BE", "BE"),
                    ("BEd", "BEd"),
                    ("BSc", "BSc"),
                    ("MA", "MA"),
                    ("MSc", "MSc"),
                    ("MBS", "MBS"),
                    ("ME", "ME"),
                    ("PhD", "PhD"),
                    ("Others", "Others"),
                ],
                max_length=45,
            ),
        ),
    ]
