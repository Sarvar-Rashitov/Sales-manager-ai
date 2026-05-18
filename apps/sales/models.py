from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import Organization, User
from apps.crm.models import Lead, Contact


class Proposal(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="proposals")
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name="proposals")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="proposals")
    title = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valid_until = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "proposals"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
