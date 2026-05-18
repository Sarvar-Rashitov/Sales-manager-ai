"""
Lead service - create, update, qualify, score leads.
"""
import logging
from django.utils import timezone
from apps.accounts.models import User, Organization
from ..models import Lead, Contact, Company, Activity

logger = logging.getLogger("apps.crm")


class LeadService:

    @staticmethod
    def create_lead(
        organization: Organization,
        title: str,
        source: str = Lead.Source.MANUAL,
        contact: Contact = None,
        company: Company = None,
        assigned_to: User = None,
        notes: str = "",
    ) -> Lead:
        lead = Lead.objects.create(
            organization=organization,
            title=title,
            source=source,
            contact=contact,
            company=company,
            assigned_to=assigned_to,
            notes=notes,
        )
        Activity.objects.create(
            organization=organization,
            lead=lead,
            activity_type=Activity.ActivityType.NOTE,
            description=f"Lead created from {source}",
        )
        logger.info("Lead created: %s [org=%s]", title, organization.id)
        return lead

    @staticmethod
    def update_status(lead: Lead, new_status: str, user: User = None) -> Lead:
        old_status = lead.status
        lead.status = new_status
        if new_status == Lead.Status.CONTACTED:
            lead.last_contacted_at = timezone.now()
        lead.save(update_fields=["status", "last_contacted_at", "updated_at"])

        Activity.objects.create(
            organization=lead.organization,
            lead=lead,
            user=user,
            activity_type=Activity.ActivityType.STATUS_CHANGE,
            description=f"Status changed: {old_status} -> {new_status}",
        )
        return lead

    @staticmethod
    def update_score(lead: Lead, score: int) -> Lead:
        lead.score = max(0, min(100, score))
        lead.save(update_fields=["score", "updated_at"])
        return lead

    @staticmethod
    def update_ai_summary(lead: Lead, summary: str, interests: list = None) -> Lead:
        lead.ai_summary = summary
        if interests is not None:
            lead.interests = interests
        lead.save(update_fields=["ai_summary", "interests", "updated_at"])
        return lead

    @staticmethod
    def get_leads_for_org(organization: Organization, status: str = None):
        qs = Lead.objects.filter(organization=organization).select_related(
            "contact", "company", "assigned_to"
        )
        if status:
            qs = qs.filter(status=status)
        return qs

    @staticmethod
    def get_or_create_lead_from_telegram(
        organization: Organization,
        telegram_id: int,
        username: str = "",
        first_name: str = "",
    ) -> tuple[Lead, bool]:
        """Find or create a lead from a Telegram message."""
        contact, _ = Contact.objects.get_or_create(
            organization=organization,
            telegram_id=telegram_id,
            defaults={
                "first_name": first_name or username or str(telegram_id),
                "telegram_username": username,
            },
        )
        lead, created = Lead.objects.get_or_create(
            organization=organization,
            contact=contact,
            status__in=[
                Lead.Status.NEW, Lead.Status.CONTACTED, Lead.Status.QUALIFIED
            ],
            defaults={
                "title": f"Telegram lead - {first_name or username or telegram_id}",
                "source": Lead.Source.TELEGRAM,
            },
        )
        return lead, created
