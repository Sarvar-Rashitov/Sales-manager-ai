from django.urls import path
from . import views

app_name = "ai_agents"

urlpatterns = [
    path("chat/<uuid:lead_pk>/", views.chat_view, name="chat"),
    path("chat/<uuid:lead_pk>/send/", views.send_message, name="send_message"),
    path("chat/<uuid:lead_pk>/proposal/", views.generate_proposal, name="generate_proposal"),
    path("prompts/", views.prompt_list, name="prompt_list"),
    path("prompts/create/", views.prompt_create, name="prompt_create"),
    path("logs/", views.ai_log_list, name="log_list"),
]
