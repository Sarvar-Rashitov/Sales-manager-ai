from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("<uuid:pk>/", views.conversation_detail, name="conversation"),
]
