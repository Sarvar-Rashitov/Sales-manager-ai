"""
Follow-up service — create, schedule, and execute follow-ups.
No Celery — uses Django management command + threading.
"""
import logging
from datetime import timedelta
from django.utils import timezone
from apps.crm.models import Lead
from apps.accounts.models import Organization, User
from .models import FollowUp

logger = logging.getLogger("apps.followups")


class FollowUpService:

    @staticmethod
    def create_followup(
        lead: Lead,
        message: str,
        scheduled_at=None,
        channel: str = FollowUp.Channel.TELEGRAM,
        assigned_to: User = None,
        ai_generated: bool = False,
        delay_hours: int = 24,
    ) -> FollowUp:
        if scheduled_at is None:
            scheduled_at = timezone.now() + timedelta(hours=delay_hours)

        return FollowUp.objects.create(
            organization=lead.organization,
            lead=lead,
            message=message,
            channel=channel,
            scheduled_at=scheduled_at,
            assigned_to=assigned_to,
            ai_generated=ai_generated,
        )

    @staticmethod
    def get_due_followups():
        """Return all pending follow-ups that are due now."""
        return FollowUp.objects.filter(
            status=FollowUp.Status.PENDING,
            scheduled_at__lte=timezone.now(),
        ).select_related("lead", "lead__contact", "organization")

    @staticmethod
    def execute_followup(followup: FollowUp) -> bool:
        """Execute a single follow-up — send via the appropriate channel."""
        try:
            if followup.channel == FollowUp.Channel.TELEGRAM:
                success = FollowUpService._send_telegram(followup)
            elif followup.channel == FollowUp.Channel.EMAIL:
                success = FollowUpService._send_email(followup)
            else:
                # Manual reminder — just mark as sent
                success = True

            if success:
                followup.status = FollowUp.Status.SENT
                followup.sent_at = timezone.now()
            else:
                followup.status = FollowUp.Status.FAILED

            followup.save(update_fields=["status", "sent_at", "updated_at"])
            return success

        except Exception as e:
            followup.status = FollowUp.Status.FAILED
            followup.error_message = str(e)
            followup.save(update_fields=["status", "error_message", "updated_at"])
            logger.error("Follow-up execution failed [%s]: %s", followup.id, e)
            return False

    @staticmethod
    def _send_telegram(followup: FollowUp) -> bool:
        contact = followup.lead.contact
        if not contact or not contact.telegram_id:
            logger.warning("No Telegram ID for lead %s", followup.lead.id)
            return False

        # Find an active Telegram account for this org
        from apps.telegram_bot.models import TelegramAccount
        from apps.telegram_bot.services.message_service import MessageService

        account = TelegramAccount.objects.filter(
            organization=followup.organization,
            status=TelegramAccount.Status.ACTIVE,
            is_ai_enabled=True,
        ).first()

        if not account:
            logger.warning("No active Telegram account for org %s", followup.organization.id)
            return False

        return MessageService.send_message(account, contact.telegram_id, followup.message)

    @staticmethod
    def _send_email(followup: FollowUp) -> bool:
        from django.core.mail import send_mail
        from django.conf import settings

        contact = followup.lead.contact
        if not contact or not contact.email:
            return False

        send_mail(
            subject=f"Follow-up from {followup.organization.name}",
            message=followup.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact.email],
            fail_silently=False,
        )
        return True

    @staticmethod
    def generate_ai_followup(lead: Lead, delay_hours: int = 24) -> FollowUp:
        """Use AI to generate and schedule a follow-up message."""
        from apps.ai_agents.services.followup_agent import FollowUpAgent
        agent = FollowUpAgent(lead)
        message = agent.run()
        return FollowUpService.create_followup(
            lead=lead,
            message=message,
            delay_hours=delay_hours,
            ai_generated=True,
        )

    @staticmethod
    def schedule_abandoned_lead_followups(days_inactive: int = 3) -> int:
        """Find leads with no recent contact and schedule AI follow-ups."""
        cutoff = timezone.now() - timedelta(days=days_inactive)
        abandoned_leads = Lead.objects.filter(
            status__in=[Lead.Status.CONTACTED, Lead.Status.QUALIFIED],
            last_contacted_at__lt=cutoff,
        ).exclude(
            followups__status=FollowUp.Status.PENDING
        )

        count = 0
        for lead in abandoned_leads:
            FollowUpService.generate_ai_followup(lead, delay_hours=1)
            count += 1

        logger.info("Scheduled %d abandoned lead follow-ups", count)
        return count
