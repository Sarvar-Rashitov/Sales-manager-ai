from rest_framework import serializers
from .models import TelegramAccount, TelegramMessage


class TelegramAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramAccount
        fields = ["id", "phone_number", "username", "first_name", "status",
                  "is_ai_enabled", "messages_sent_today", "daily_message_limit", "created_at"]
        read_only_fields = ["id", "status", "messages_sent_today", "created_at"]


class TelegramMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramMessage
        fields = ["id", "sender_name", "sender_username", "text", "direction",
                  "ai_processed", "ai_response", "created_at"]
        read_only_fields = fields
