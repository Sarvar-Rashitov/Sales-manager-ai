from django.contrib import admin
from .models import TelegramAccount, TelegramSession, TelegramBot, TelegramMessage, Broadcast, BroadcastRecipient


@admin.register(TelegramAccount)
class TelegramAccountAdmin(admin.ModelAdmin):
    list_display = ["phone_number", "username", "status", "is_ai_enabled",
                    "messages_sent_today", "daily_message_limit", "organization"]
    list_filter = ["status", "is_ai_enabled", "organization"]
    search_fields = ["phone_number", "username"]
    readonly_fields = ["session_string", "telegram_user_id"]


@admin.register(TelegramBot)
class TelegramBotAdmin(admin.ModelAdmin):
    list_display = ["name", "bot_username", "status", "is_ai_enabled",
                    "messages_sent_today", "daily_message_limit", "organization"]
    list_filter = ["status", "is_ai_enabled", "organization"]
    search_fields = ["name", "bot_username"]
    readonly_fields = ["bot_token", "bot_id", "webhook_secret", "last_error"]


@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = ["sender_name", "source", "direction", "text_preview", "ai_processed", "created_at"]
    list_filter = ["direction", "source", "ai_processed"]
    search_fields = ["sender_name", "sender_username", "text"]

    def text_preview(self, obj):
        return obj.text[:60]
    text_preview.short_description = "Text"


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ["name", "channel", "status", "total_recipients",
                    "sent_count", "failed_count", "success_rate", "created_at"]
    list_filter = ["status", "channel", "organization"]
    readonly_fields = ["sent_count", "failed_count", "total_recipients", "started_at", "completed_at"]


@admin.register(BroadcastRecipient)
class BroadcastRecipientAdmin(admin.ModelAdmin):
    list_display = ["broadcast", "lead", "telegram_id", "status", "sent_at"]
    list_filter = ["status"]
    readonly_fields = ["sent_at"]
