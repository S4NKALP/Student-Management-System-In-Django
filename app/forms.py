from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import SetPasswordForm
from app.models import (
    Staff,
    Student,
    Parent,
    StaffInstituteFeedback,
    ParentInstituteFeedback,
)
from django.contrib.auth.models import Group


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
            student.set_password(new_password)
        # Set default password to '123' for new students if no password provided
        elif not student.pk and not student.password:  # New student without password
            student.set_password("123")

        if commit:
            student.save()

            # Make sure student has Student group
            if (
                hasattr(student, "groups")
                and not student.groups.filter(name="Student").exists()
            ):
                student_group = Group.objects.filter(name="Student").first()
                if student_group:
                    student.groups.add(student_group)

            # Handle parent creation/update for both new and existing students
            if student.parent_name and student.parent_phone:
                try:
                    # Check if parent already exists
                    parent = Parent.objects.filter(phone=student.parent_phone).first()

                    if not parent:
                        # Create new parent
                        parent = Parent.objects.create(
                            name=student.parent_name,
                            phone=student.parent_phone,
                            password=make_password("123"),  # Default password
                        )

                        # Add Parent group to new parent
                        parent_group = Group.objects.filter(name="Parent").first()
                        if parent_group:
                            parent.groups.add(parent_group)

                    # Add student to parent's students
                    parent.students.add(student)

                except Exception as e:
                    # Log the error but don't prevent student creation
                    print(f"Error creating/updating parent: {str(e)}")

        return student


class StaffAdminForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text="Enter a new password if you want to reset it. Leave blank otherwise. Default is '123'.",
    )

    class Meta:
        model = Staff
        fields = "__all__"  # Include all fields, including groups

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
            self.save_m2m()  # Save many-to-many relationships including groups

            # If groups were not selected in the form, ensure staff has Teacher group
            if not staff.groups.exists():
                teacher_group = Group.objects.filter(name="Teacher").first()
                if teacher_group:
                    staff.groups.add(teacher_group)

        return staff


class ParentAdminForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text="Enter a new password if you want to reset it. Leave blank otherwise. Default is '123'.",
    )

    class Meta:
        model = Parent
        fields = "__all__"

    def save(self, commit=True):
        parent = super().save(commit=False)
        new_password = self.cleaned_data.get("new_password")

        if new_password:
            parent.password = make_password(new_password)
        # Set default password to '123' for new parents if no password provided
        elif not parent.pk and not parent.password:  # New parent without password
            parent.password = make_password("123")

        if commit:
            parent.save()
        return parent


class StaffInstituteFeedbackForm(forms.ModelForm):
    class Meta:
        model = StaffInstituteFeedback
        fields = [
            "feedback_type",
            "rating",
            "feedback_text",
            "is_anonymous",
            "is_public",
        ]
        widgets = {
            "feedback_text": forms.Textarea(attrs={"rows": 4}),
            "rating": forms.NumberInput(attrs={"step": "0.5", "min": "1", "max": "5"}),
        }


class ParentInstituteFeedbackForm(forms.ModelForm):
    class Meta:
        model = ParentInstituteFeedback
        fields = [
            "feedback_type",
            "rating",
            "feedback_text",
            "is_anonymous",
            "is_public",
        ]
        widgets = {
            "feedback_text": forms.Textarea(attrs={"rows": 4}),
            "rating": forms.NumberInput(attrs={"step": "0.5", "min": "1", "max": "5"}),
        }
