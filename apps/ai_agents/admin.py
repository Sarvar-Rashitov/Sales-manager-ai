from django.contrib import admin
from .models import Prompt, AILog, ConversationMemory, OutreachCampaign, OutreachLog


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ["name", "agent_type", "is_active", "is_default", "organization"]
    list_filter = ["agent_type", "is_active", "organization"]
    search_fields = ["name"]


@admin.register(AILog)
class AILogAdmin(admin.ModelAdmin):
    list_display = ["agent_type", "model", "total_tokens", "latency_ms", "success", "created_at"]
    list_filter = ["agent_type", "success", "model"]
    readonly_fields = ["created_at"]


@admin.register(ConversationMemory)
class ConversationMemoryAdmin(admin.ModelAdmin):
    list_display = ["lead", "detected_language", "sentiment_score", "buying_intent_score", "updated_at"]
    readonly_fields = ["messages", "summary"]


@admin.register(OutreachCampaign)
class OutreachCampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "sent_count", "reply_count", "created_by"]
    list_filter = ["status"]
