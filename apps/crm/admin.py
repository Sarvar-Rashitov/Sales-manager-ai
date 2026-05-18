from django.contrib import admin
from .models import Company, Contact, Lead, Pipeline, PipelineStage, Deal, Task, Note, Activity


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name", "industry", "country", "organization"]
    search_fields = ["name"]
    list_filter = ["industry", "organization"]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "phone", "telegram_username", "company", "organization"]
    search_fields = ["first_name", "last_name", "email", "telegram_username"]
    list_filter = ["organization"]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "source", "score", "assigned_to", "organization", "created_at"]
    list_filter = ["status", "source", "organization"]
    search_fields = ["title"]
    readonly_fields = ["ai_summary", "score"]


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "is_default"]


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ["name", "pipeline", "order", "probability"]


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ["title", "value", "status", "pipeline_stage", "assigned_to"]
    list_filter = ["status", "organization"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "priority", "due_date", "completed", "assigned_to"]
    list_filter = ["completed", "priority"]


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["activity_type", "description", "user", "lead", "created_at"]
    list_filter = ["activity_type", "organization"]
    readonly_fields = ["created_at"]
