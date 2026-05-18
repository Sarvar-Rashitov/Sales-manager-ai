from django.contrib import admin
from .models import DailyStats


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ["date", "organization", "new_leads", "won_deals", "revenue", "ai_responses"]
    list_filter = ["organization"]
    ordering = ["-date"]
