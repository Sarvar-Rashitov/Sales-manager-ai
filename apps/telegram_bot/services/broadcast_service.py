"""
Broadcast service — ommaviy xabar yuborish.
Userbot (MTProto) yoki Bot API orqali ishlaydi.
Celery yo'q — management command yoki to'g'ridan-to'g'ri chaqiriladi.
"""
import logging
from django.utils import timezone
from apps.crm.models import Lead
from ..models import Broadcast, BroadcastRecipient, TelegramAccount, TelegramBot

logger = logging.getLogger("apps.telegram_bot")


class BroadcastService:

    @staticmethod
    def prepare(broadcast: Broadcast) -> int:
        """
        Broadcast uchun qabul qiluvchilar ro'yxatini tuzadi.
        Qaytaradi: qabul qiluvchilar soni.
        """
        # Avvalgi pending recipientlarni o'chiramiz
        broadcast.recipients.filter(status=BroadcastRecipient.Status.PENDING).delete()

        if broadcast.target_all_leads:
            leads = Lead.objects.filter(organization=broadcast.organization)
        else:
            leads = broadcast.target_leads.all()

        recipients = []
        for lead in leads:
            contact = lead.contact
            tg_id = contact.telegram_id if contact else None
            status = (
                BroadcastRecipient.Status.PENDING if tg_id
                else BroadcastRecipient.Status.SKIPPED
            )
            # Xabarni personalizatsiya qilamiz
            name = contact.full_name if contact else "there"
            personalized = broadcast.message_text.replace("{name}", name)

            recipients.append(BroadcastRecipient(
                broadcast=broadcast,
                lead=lead,
                telegram_id=tg_id,
                status=status,
                personalized_message=personalized,
            ))

        BroadcastRecipient.objects.bulk_create(recipients, ignore_conflicts=True)
        count = len([r for r in recipients if r.status == BroadcastRecipient.Status.PENDING])
        broadcast.total_recipients = count
        broadcast.save(update_fields=["total_recipients"])
        return count

    @staticmethod
    def run(broadcast: Broadcast) -> dict:
        """
        Broadcastni ishga tushiradi.
        Sinxron — management command yoki view'dan chaqiriladi.
        """
        broadcast.status = Broadcast.Status.RUNNING
        broadcast.started_at = timezone.now()
        broadcast.save(update_fields=["status", "started_at"])

        pending = broadcast.recipients.filter(status=BroadcastRecipient.Status.PENDING)
        sent = 0
        failed = 0

        for recipient in pending:
            success = BroadcastService._send_to_recipient(broadcast, recipient)
            if success:
                sent += 1
            else:
                failed += 1

        broadcast.sent_count = sent
        broadcast.failed_count = failed
        broadcast.status = Broadcast.Status.COMPLETED
        broadcast.completed_at = timezone.now()
        broadcast.save(update_fields=["sent_count", "failed_count", "status", "completed_at"])

        logger.info("Broadcast '%s' completed: %d sent, %d failed", broadcast.name, sent, failed)
        return {"sent": sent, "failed": failed, "total": sent + failed}

    @staticmethod
    def _send_to_recipient(broadcast: Broadcast, recipient: BroadcastRecipient) -> bool:
        text = recipient.personalized_message or broadcast.message_text
        success = False

        try:
            if broadcast.channel == Broadcast.Channel.BOT and broadcast.bot:
                from .bot_service import BotService
                success = BotService.send_message(
                    broadcast.bot, recipient.telegram_id, text,
                    parse_mode=broadcast.parse_mode,
                )
            elif broadcast.channel == Broadcast.Channel.USERBOT and broadcast.userbot_account:
                from .message_service import MessageService
                success = MessageService.send_message(
                    broadcast.userbot_account, recipient.telegram_id, text
                )
        except Exception as e:
            logger.error("Broadcast send error [recipient=%s]: %s", recipient.id, e)
            recipient.error_message = str(e)

        recipient.status = (
            BroadcastRecipient.Status.SENT if success
            else BroadcastRecipient.Status.FAILED
        )
        if success:
            recipient.sent_at = timezone.now()
        recipient.save(update_fields=["status", "sent_at", "error_message"])
        return success

    @staticmethod
    def cancel(broadcast: Broadcast) -> None:
        broadcast.status = Broadcast.Status.CANCELLED
        broadcast.save(update_fields=["status"])
        broadcast.recipients.filter(
            status=BroadcastRecipient.Status.PENDING
        ).update(status=BroadcastRecipient.Status.SKIPPED)
