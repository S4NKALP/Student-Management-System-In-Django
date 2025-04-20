from django.shortcuts import render


# Error handler views
def handler400(request, exception=None):
    """Bad request error handler"""
    return render(request, "400.html", status=400)


def handler403(request, exception=None):
    """Forbidden error handler"""
    return render(request, "403.html", status=403)


def handler404(request, exception=None):
    """Page not found error handler"""
    return render(request, "404.html", status=404)


def handler500(request):
    """Server error handler"""
    return render(request, "500.html", status=500)


def handler505(request, exception=None):
    """HTTP version not supported error handler"""
    return render(request, "505.html", status=505)
