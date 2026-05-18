from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import Organization


class DailyStats(BaseModel):
    """Pre-aggregated daily statistics per organization."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="daily_stats")
    date = models.DateField()
    new_leads = models.PositiveIntegerField(default=0)
    qualified_leads = models.PositiveIntegerField(default=0)
    won_deals = models.PositiveIntegerField(default=0)
    lost_deals = models.PositiveIntegerField(default=0)
    messages_sent = models.PositiveIntegerField(default=0)
    ai_responses = models.PositiveIntegerField(default=0)
    followups_sent = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = "daily_stats"
        unique_together = [("organization", "date")]
        ordering = ["-date"]
