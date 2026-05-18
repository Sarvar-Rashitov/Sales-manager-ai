"""
Real-time messaging models — conversations and messages for live chat.
"""
from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import User, Organization
from apps.crm.models import Lead


class Conversation(BaseModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        RESOLVED = "resolved", "Resolved"
        AI_HANDLED = "ai_handled", "AI Handled"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="conversations")
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name="conversations")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="conversations")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    channel = models.CharField(max_length=20, default="web")  # web, telegram, email
    unread_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "conversations"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation {self.id} [{self.status}]"


class Message(BaseModel):
    class SenderType(models.TextChoices):
        USER = "user", "User"
        AI = "ai", "AI Agent"
        OPERATOR = "operator", "Operator"

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender_type = models.CharField(max_length=10, choices=SenderType.choices)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_messages")
    content = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = "messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender_type}: {self.content[:50]}"
