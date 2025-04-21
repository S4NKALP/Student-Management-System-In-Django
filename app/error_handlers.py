import logging
from django.shortcuts import render
from django.conf import settings
from django.http import HttpRequest
from typing import Optional, Any
import traceback

logger = logging.getLogger(__name__)

def get_error_context(request: HttpRequest, exception: Optional[Exception] = None, status_code: int = 500) -> dict:
    """Generate context for error pages with relevant information"""
    context = {
        'status_code': status_code,
        'request_path': request.path,
        'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
        'ip_address': request.META.get('REMOTE_ADDR', 'Unknown'),
    }
    
    if exception:
        context.update({
            'error_message': str(exception),
            'error_type': exception.__class__.__name__,
        })
        
        # Only include traceback in development
        if settings.DEBUG:
            context['traceback'] = traceback.format_exc()
    
    return context

def handler400(request: HttpRequest, exception: Optional[Exception] = None) -> Any:
    """Bad request error handler"""
    logger.warning(
        f"400 Bad Request: {request.path}",
        extra={
            'exception': str(exception) if exception else None,
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'ip_address': request.META.get('REMOTE_ADDR'),
        }
    )
    context = get_error_context(request, exception, 400)
    return render(request, "400.html", context, status=400)

def handler403(request: HttpRequest, exception: Optional[Exception] = None) -> Any:
    """Forbidden error handler"""
    logger.warning(
        f"403 Forbidden: {request.path}",
        extra={
            'exception': str(exception) if exception else None,
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'ip_address': request.META.get('REMOTE_ADDR'),
        }
    )
    context = get_error_context(request, exception, 403)
    return render(request, "403.html", context, status=403)

def handler404(request: HttpRequest, exception: Optional[Exception] = None) -> Any:
    """Page not found error handler"""
    logger.warning(
        f"404 Not Found: {request.path}",
        extra={
            'exception': str(exception) if exception else None,
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'ip_address': request.META.get('REMOTE_ADDR'),
        }
    )
    context = get_error_context(request, exception, 404)
    return render(request, "404.html", context, status=404)

def handler500(request: HttpRequest) -> Any:
    """Server error handler"""
    logger.error(
        f"500 Server Error: {request.path}",
        exc_info=True,
        extra={
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'ip_address': request.META.get('REMOTE_ADDR'),
        }
    )
    context = get_error_context(request, None, 500)
    return render(request, "500.html", context, status=500)

def handler505(request: HttpRequest, exception: Optional[Exception] = None) -> Any:
    """HTTP version not supported error handler"""
    logger.error(
        f"505 HTTP Version Not Supported: {request.path}",
        extra={
            'exception': str(exception) if exception else None,
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'ip_address': request.META.get('REMOTE_ADDR'),
        }
    )
    context = get_error_context(request, exception, 505)
    return render(request, "505.html", context, status=505)
