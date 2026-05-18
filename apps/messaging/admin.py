from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "channel", "lead", "assigned_to", "unread_count", "updated_at"]
    list_filter = ["status", "channel"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["sender_type", "content_preview", "conversation", "created_at"]
    list_filter = ["sender_type"]

    def content_preview(self, obj):
        return obj.content[:60]
