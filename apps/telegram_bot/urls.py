from django.urls import path
from . import views

app_name = "telegram"

urlpatterns = [
    # Userbot accounts
    path("accounts/", views.account_list, name="account_list"),
    path("accounts/add/", views.account_add, name="account_add"),
    path("accounts/<uuid:pk>/verify/", views.verify_code, name="verify_code"),
    path("accounts/<uuid:pk>/2fa/", views.verify_2fa, name="verify_2fa"),
    path("accounts/<uuid:pk>/disconnect/", views.disconnect_account, name="disconnect"),

    # Bot API
    path("bots/add/", views.bot_add, name="bot_add"),
    path("bots/<uuid:pk>/webhook/setup/", views.bot_webhook_setup, name="bot_webhook"),
    path("bots/<uuid:pk>/webhook/delete/", views.bot_delete_webhook, name="bot_webhook_delete"),

    # Webhook endpoint (CSRF exempt, Telegram calls this)
    path("bot/<uuid:pk>/webhook/", views.bot_webhook_handler, name="bot_webhook_handler"),

    # Broadcast
    path("broadcast/", views.broadcast_list, name="broadcast_list"),
    path("broadcast/create/", views.broadcast_create, name="broadcast_create"),
    path("broadcast/<uuid:pk>/", views.broadcast_detail, name="broadcast_detail"),
    path("broadcast/<uuid:pk>/run/", views.broadcast_run, name="broadcast_run"),
    path("broadcast/<uuid:pk>/cancel/", views.broadcast_cancel, name="broadcast_cancel"),

    # Inbox
    path("inbox/", views.message_inbox, name="inbox"),
]
