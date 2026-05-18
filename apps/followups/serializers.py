from rest_framework import serializers
from .models import FollowUp


class FollowUpSerializer(serializers.ModelSerializer):
    lead_title = serializers.CharField(source="lead.title", read_only=True)

    class Meta:
        model = FollowUp
        fields = ["id", "lead", "lead_title", "message", "channel", "status",
                  "scheduled_at", "sent_at", "ai_generated", "created_at"]
        read_only_fields = ["id", "status", "sent_at", "created_at"]
