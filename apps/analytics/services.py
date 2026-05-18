"""
Analytics service — computes stats from CRM data.
"""
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from apps.accounts.models import Organization
from apps.crm.models import Lead, Deal
from apps.ai_agents.models import AILog
from apps.followups.models import FollowUp


class AnalyticsService:

    @staticmethod
    def get_dashboard_stats(organization: Organization) -> dict:
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        leads = Lead.objects.filter(organization=organization)
        deals = Deal.objects.filter(organization=organization)

        total_leads = leads.count()
        new_this_month = leads.filter(created_at__gte=thirty_days_ago).count()
        qualified = leads.filter(status=Lead.Status.QUALIFIED).count()
        won = leads.filter(status=Lead.Status.WON).count()
        lost = leads.filter(status=Lead.Status.LOST).count()

        conversion_rate = round((won / total_leads * 100), 1) if total_leads > 0 else 0

        total_revenue = deals.filter(status=Deal.Status.WON).aggregate(
            total=Sum("value")
        )["total"] or 0

        avg_lead_score = leads.aggregate(avg=Avg("score"))["avg"] or 0

        ai_calls_today = AILog.objects.filter(
            organization=organization,
            created_at__date=now.date(),
        ).count()

        pending_followups = FollowUp.objects.filter(
            organization=organization,
            status=FollowUp.Status.PENDING,
        ).count()

        return {
            "total_leads": total_leads,
            "new_this_month": new_this_month,
            "qualified": qualified,
            "won": won,
            "lost": lost,
            "conversion_rate": conversion_rate,
            "total_revenue": float(total_revenue),
            "avg_lead_score": round(float(avg_lead_score), 1),
            "ai_calls_today": ai_calls_today,
            "pending_followups": pending_followups,
        }

    @staticmethod
    def get_funnel_data(organization: Organization) -> list[dict]:
        """Sales funnel — count of leads at each stage."""
        stages = [
            Lead.Status.NEW,
            Lead.Status.CONTACTED,
            Lead.Status.QUALIFIED,
            Lead.Status.DEMO,
            Lead.Status.NEGOTIATION,
            Lead.Status.WON,
        ]
        funnel = []
        for stage in stages:
            count = Lead.objects.filter(organization=organization, status=stage).count()
            funnel.append({"stage": stage, "label": stage.title(), "count": count})
        return funnel

    @staticmethod
    def get_lead_trend(organization: Organization, days: int = 30) -> list[dict]:
        """Daily lead creation trend."""
        from django.db.models.functions import TruncDate
        cutoff = timezone.now() - timedelta(days=days)
        data = (
            Lead.objects.filter(organization=organization, created_at__gte=cutoff)
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )
        return list(data)

    @staticmethod
    def get_source_breakdown(organization: Organization) -> list[dict]:
        data = (
            Lead.objects.filter(organization=organization)
            .values("source")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        return list(data)
