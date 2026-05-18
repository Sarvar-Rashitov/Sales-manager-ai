"""
Follow-up models — scheduled reminders and outreach.
"""
from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import User, Organization
from apps.crm.models import Lead, Contact


class FollowUp(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    class Channel(models.TextChoices):
        TELEGRAM = "telegram", "Telegram"
        EMAIL = "email", "Email"
        MANUAL = "manual", "Manual Reminder"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="followups")
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="followups")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="followups")

    message = models.TextField()
    channel = models.CharField(max_length=20, choices=Channel.choices, default=Channel.TELEGRAM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    ai_generated = models.BooleanField(default=False)

    class Meta:
        db_table = "followups"
        ordering = ["scheduled_at"]
        indexes = [
            models.Index(fields=["status", "scheduled_at"]),
            models.Index(fields=["organization", "status"]),
        ]

    def __str__(self):
        return f"Follow-up for {self.lead} at {self.scheduled_at:%Y-%m-%d %H:%M}"
