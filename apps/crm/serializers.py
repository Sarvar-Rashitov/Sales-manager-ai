from rest_framework import serializers
from .models import Lead, Contact, Company, Deal, Task, Note, Activity, Pipeline, PipelineStage


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "website", "industry", "size", "country", "created_at"]
        read_only_fields = ["id", "created_at"]


class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Contact
        fields = ["id", "full_name", "first_name", "last_name", "email", "phone",
                  "telegram_username", "telegram_id", "company", "position", "created_at"]
        read_only_fields = ["id", "created_at"]


class LeadSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.full_name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True)

    class Meta:
        model = Lead
        fields = ["id", "title", "status", "source", "score", "budget", "notes",
                  "ai_summary", "interests", "contact", "contact_name",
                  "assigned_to", "assigned_to_name", "last_contacted_at",
                  "created_at", "updated_at"]
        read_only_fields = ["id", "score", "ai_summary", "created_at", "updated_at"]


class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ["id", "title", "value", "status", "pipeline_stage", "expected_close_date",
                  "notes", "lead", "contact", "assigned_to", "created_at"]
        read_only_fields = ["id", "created_at"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "priority", "due_date", "completed",
                  "completed_at", "lead", "deal", "assigned_to", "created_at"]
        read_only_fields = ["id", "created_at"]


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ["id", "activity_type", "description", "metadata", "user", "lead",
                  "contact", "deal", "created_at"]
        read_only_fields = ["id", "created_at"]
