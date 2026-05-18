"""
Global template context — injects data available in every template.
"""
from django.conf import settings


def global_context(request):
    return {
        "APP_NAME": "AI Sales Manager",
        "DEBUG": settings.DEBUG,
        "user_org": getattr(getattr(request, "user", None), "organization", None),
    }
