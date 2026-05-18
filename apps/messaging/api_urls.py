from django.urls import path
from . import api_views

urlpatterns = [
    path("conversations/", api_views.conversation_list_api, name="api_conversations"),
]
