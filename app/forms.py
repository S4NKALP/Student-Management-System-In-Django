from django import forms
from .models import Subject, Course


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name", "course", "duration"]  # Include 'name' field here

    # Optionally, you can add custom validation if needed.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "course"
        ].queryset = (
            Course.objects.all()
        )  # Dynamically set the course queryset if needed
