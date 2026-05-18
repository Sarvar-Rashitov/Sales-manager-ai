from django.contrib import admin
from .models import Proposal


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "total_value", "lead", "created_by", "created_at"]
    list_filter = ["status"]
    search_fields = ["title"]
