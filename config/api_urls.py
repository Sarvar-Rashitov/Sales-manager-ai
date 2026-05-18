"""
API v1 URL routing — all DRF endpoints live here.
"""
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # JWT
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # App APIs
    path("accounts/", include("apps.accounts.api_urls")),
    path("crm/", include("apps.crm.api_urls")),
    path("telegram/", include("apps.telegram_bot.api_urls")),
    path("ai/", include("apps.ai_agents.api_urls")),
    path("analytics/", include("apps.analytics.api_urls")),
    path("messaging/", include("apps.messaging.api_urls")),
    path("knowledge/", include("apps.knowledge_base.api_urls")),
    path("followups/", include("apps.followups.api_urls")),
    path("sales/", include("apps.sales.api_urls")),
]
