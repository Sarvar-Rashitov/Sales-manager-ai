from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Organization, OrganizationSettings, TeamInvite


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "created_at"]
    search_fields = ["name", "slug"]
    list_filter = ["is_active"]


@admin.register(OrganizationSettings)
class OrganizationSettingsAdmin(admin.ModelAdmin):
    list_display = ["organization", "ai_enabled", "openai_model", "ai_language"]
    readonly_fields = ["openai_api_key", "telegram_api_hash", "telegram_bot_token"]
    fieldsets = (
        ("Organization", {"fields": ("organization",)}),
        ("OpenAI", {"fields": ("openai_api_key", "openai_model", "openai_embedding_model")}),
        ("Telegram MTProto", {"fields": ("telegram_api_id", "telegram_api_hash")}),
        ("AI Behaviour", {"fields": ("ai_enabled", "ai_reply_delay_min", "ai_reply_delay_max",
                                     "daily_message_limit", "ai_language")}),
        ("Notifications", {"fields": ("notify_email", "notify_on_new_lead", "notify_on_qualified_lead")}),
        ("Branding", {"fields": ("company_description", "products_services", "support_contact")}),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "full_name", "role", "organization", "email_verified", "is_active"]
    list_filter = ["role", "is_active", "email_verified", "organization"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["email"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": ("first_name", "last_name", "avatar")}),
        ("Organization", {"fields": ("organization", "role")}),
        ("Status", {"fields": ("is_active", "is_staff", "is_superuser", "email_verified")}),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role", "organization"),
        }),
    )


@admin.register(TeamInvite)
class TeamInviteAdmin(admin.ModelAdmin):
    list_display = ["email", "organization", "role", "accepted", "expires_at"]
    list_filter = ["accepted", "role"]
    search_fields = ["email"]
