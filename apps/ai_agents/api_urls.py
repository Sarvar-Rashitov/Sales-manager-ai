from django.urls import path
from . import api_views

urlpatterns = [
    path("chat/<uuid:lead_pk>/", api_views.chat_api, name="api_chat"),
    path("proposal/<uuid:lead_pk>/", api_views.proposal_api, name="api_proposal"),
    path("logs/", api_views.ai_logs_api, name="api_ai_logs"),
]
