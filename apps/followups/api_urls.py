from django.urls import path
from . import api_views

urlpatterns = [
    path("", api_views.followup_list_api, name="api_followups"),
]
