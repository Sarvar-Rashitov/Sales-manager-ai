"""
Audit log middleware — records every authenticated request.
"""
import logging
import time

logger = logging.getLogger("apps.common")


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = round((time.time() - start) * 1000, 2)

        user = getattr(request, "user", None)
        username = user.email if (user and user.is_authenticated) else "anonymous"

        logger.info(
            "%s %s %s | user=%s | %sms",
            request.method,
            request.path,
            response.status_code,
            username,
            duration,
        )
        return response
