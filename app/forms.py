from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import SetPasswordForm
from .models import Staff, Student


class CustomSetPasswordForm(SetPasswordForm):
    def save(self, commit=True):
        user = self.user
        user.set_password(self.cleaned_data["new_password1"])
        if commit:
            user.save()
        return user


class StudentAdminForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text="Enter a new password if you want to reset it. Leave blank otherwise. Default is '123'.",
    )

    class Meta:
        model = Student
        fields = "__all__"

    def save(self, commit=True):
        student = super().save(commit=False)
        new_password = self.cleaned_data.get("new_password")
        
        if new_password:
            student.password = make_password(new_password)
        # Set default password to '123' for new students if no password provided
        elif not student.pk and not student.password:  # New student without password
            student.password = make_password("123")
            
        if commit:
            student.save()
        return student


class StaffAdminForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text="Enter a new password if you want to reset it. Leave blank otherwise. Default is '123'.",
    )

    class Meta:
        model = Staff
        fields = "__all__"

    def save(self, commit=True):
        staff = super().save(commit=False)
        new_password = self.cleaned_data.get("new_password")
        
        if new_password:
            staff.password = make_password(new_password)
        # Set default password to '123' for new staff if no password provided
        elif not staff.pk and not staff.password:  # New staff without password
            staff.password = make_password("123")
            
        if commit:
            staff.save()
        return staff
