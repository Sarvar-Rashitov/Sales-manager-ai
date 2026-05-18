"""
Root URL configuration.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # --- Web (MVT) ---
    path("", include("apps.dashboard.urls", namespace="dashboard")),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("crm/", include("apps.crm.urls", namespace="crm")),
    path("telegram/", include("apps.telegram_bot.urls", namespace="telegram")),
    path("ai/", include("apps.ai_agents.urls", namespace="ai_agents")),
    path("analytics/", include("apps.analytics.urls", namespace="analytics")),
    path("messaging/", include("apps.messaging.urls", namespace="messaging")),
    path("knowledge/", include("apps.knowledge_base.urls", namespace="knowledge_base")),
    path("followups/", include("apps.followups.urls", namespace="followups")),
    path("sales/", include("apps.sales.urls", namespace="sales")),

    # --- REST API ---
    path("api/v1/", include("config.api_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
