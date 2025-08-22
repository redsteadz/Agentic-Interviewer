# api/middleware.py
from django.utils.deprecation import MiddlewareMixin

class DisableCSRFMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith("/webhook/vapi/") or (request.path.startswith("/api/phone-number") and request.method == "PATCH"):
            setattr(request, "_dont_enforce_csrf_checks", True)
        return None
