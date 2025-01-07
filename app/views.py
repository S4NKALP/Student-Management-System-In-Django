from django.shortcuts import render, get_object_or_404
from django.contrib.admin import site
from app.models import Student, NewsEvent, Subject


# Dashboard for admin
def dashboard(request):
    context = {
        **site.each_context(request),
        "title": "Dashboard",
        # "breadcrumbs": [{"name": "Dashboard", "url": "dashboard"}],
    }
    return render(request, "dashboard.html", context)


# Student-specific dashboard
def studentdashboard(request):
    context = {
        **site.each_context(request),
        "title": "Student Dashboard",
    }

    if request.user.is_authenticated:
        news_events = NewsEvent.objects.all()
        subjects = Subject.objects.all()
        context["news_events"] = news_events
        context["subjects"] = subjects

    return render(request, "studentdashboard.html", context)
