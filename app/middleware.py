from django.http import HttpResponse
from django.template.loader import render_to_string


class HTTP505Middleware:
    """
    Middleware to handle HTTP 505 errors (HTTP Version Not Supported)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request and get the response
        response = self.get_response(request)
        return response

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
