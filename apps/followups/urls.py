from django.urls import path
from . import views

app_name = "followups"

urlpatterns = [
    path("", views.followup_list, name="followup_list"),
    path("create/", views.followup_create, name="followup_create"),
    path("ai/<uuid:lead_pk>/", views.generate_ai_followup, name="generate_ai"),
]
