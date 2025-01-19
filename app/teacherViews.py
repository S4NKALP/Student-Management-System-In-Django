from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def teacher_dashboard(request):
    return render(request, "teacher/dashboard.html")
