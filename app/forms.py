from django import forms
from django.contrib.auth.hashers import make_password
from .models import Staff, Student


class StudentAdminForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text="Enter a new password if you want to reset it. Leave blank otherwise.",
    )

    class Meta:
        model = Student
        fields = "__all__"

    def save(self, commit=True):
        student = super().save(commit=False)
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            student.password = make_password(new_password)
        if commit:
            student.save()
        return student


class StaffAdminForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text="Enter a new password if you want to reset it. Leave blank otherwise.",
    )

    class Meta:
        model = Staff
        fields = "__all__"

    def save(self, commit=True):
        student = super().save(commit=False)
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            student.password = make_password(new_password)
        if commit:
            student.save()
        return student
