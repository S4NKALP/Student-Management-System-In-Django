from django import forms
from django.utils.translation import gettext_lazy as _

from app.models import Course, Marksheet, Subject

# class MarksheetForm(forms.ModelForm):
#     class Meta:
#         model = Marksheet
#         fields = "__all__"
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         if self.instance.pk and self.instance.course:
#             self.fields["subject"].queryset = Subject.objects.filter(
#                 course=self.instance.course,
#                 semester_or_year_number=self.instance.period_number,
#             )
#         # else:
#         # self.fields["subject"].queryset = Subject.objects.none()


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name", "course", "semester_or_year_number", "teacher"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "course" in self.data:
            try:
                course_id = int(self.data.get("course"))
                course = Course.objects.get(pk=course_id)
                self.fields["semester_or_year_number"].choices = [
                    (i, i) for i in range(1, course.duration + 1)
                ]
            except (ValueError, Course.DoesNotExist):
                pass
        elif self.instance.pk:
            course = self.instance.course
            self.fields["semester_or_year_number"].choices = [
                (i, i) for i in range(1, course.duration + 1)
            ]
