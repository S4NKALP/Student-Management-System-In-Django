from django.http import HttpResponse, HttpResponseServerError
from django.template.loader import render_to_string
import re
from django.middleware.csrf import CsrfViewMiddleware


class HTTP505Middleware:
    """
    Middleware to handle HTTP 505 errors (HTTP Version Not Supported)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Simple check for HTTP version
        http_version = request.META.get("SERVER_PROTOCOL", "")
        if http_version and http_version.startswith("HTTP/") and http_version > "HTTP/2.0":
            # This is a simplistic check - in reality, you'd want to handle this more gracefully
            return HttpResponseServerError("HTTP Version Not Supported", content_type="text/plain")
        
        return self.get_response(request)

    def process_exception(self, request, exception):
        # Check if exception is related to HTTP version
        if hasattr(exception, "status_code") and exception.status_code == 505:
            # Render our 505 template
            context = {
                "request_path": request.path,
                "request_method": request.method,
                "user": request.user,
            }
            response_content = render_to_string("505.html", context, request)
            return HttpResponse(response_content, status=505)
        return None


class CSRFExemptMiddleware(CsrfViewMiddleware):
    """
    Middleware to exempt specific URLs from CSRF protection.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            re.compile(r'^/saveFCMToken/$'),
        ]
        super().__init__(get_response)
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Check if the path matches any of the exempt URLs
        path = request.path_info
        if any(url.match(path) for url in self.exempt_urls):
            return None  # Skip CSRF validation
        
        # Otherwise, continue with regular CSRF validation
        return super().process_view(request, callback, callback_args, callback_kwargs)
