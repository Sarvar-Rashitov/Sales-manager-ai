from django.urls import path
from . import api_views

urlpatterns = [
    path("accounts/", api_views.account_list_api, name="api_tg_accounts"),
    path("messages/", api_views.message_list_api, name="api_tg_messages"),
]
