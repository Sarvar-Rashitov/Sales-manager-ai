from rest_framework import serializers
from .models import AILog, Prompt, ConversationMemory


class AILogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AILog
        fields = ["id", "agent_type", "model", "total_tokens", "latency_ms",
                  "success", "created_at"]
        read_only_fields = fields


class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = ["id", "name", "agent_type", "system_prompt", "is_active", "is_default"]
        read_only_fields = ["id"]


class ConversationMemorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMemory
        fields = ["id", "messages", "summary", "detected_language",
                  "sentiment_score", "buying_intent_score", "extracted_budget",
                  "extracted_interests", "last_agent", "updated_at"]
        read_only_fields = fields
