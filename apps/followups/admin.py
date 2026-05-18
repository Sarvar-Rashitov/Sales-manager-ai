from django.contrib import admin
from .models import FollowUp


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ["lead", "channel", "status", "scheduled_at", "sent_at", "ai_generated"]
    list_filter = ["status", "channel", "ai_generated"]
    search_fields = ["lead__title", "message"]
    readonly_fields = ["sent_at"]
