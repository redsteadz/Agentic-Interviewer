# api/middleware.py
from django.utils.deprecation import MiddlewareMixin

class DisableCSRFMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith("/webhook/vapi/"):
            setattr(request, "_dont_enforce_csrf_checks", True)
        return None
