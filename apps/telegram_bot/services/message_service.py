"""
Telegram message sending service with human-like delays and anti-spam.
"""
import asyncio
import random
import logging
from django.utils import timezone
from ..models import TelegramAccount, TelegramMessage

logger = logging.getLogger("apps.telegram_bot")


class MessageService:

    @staticmethod
    def send_message(account: TelegramAccount, chat_id: int, text: str) -> bool:
        """
        Send a message via Telethon with human-like typing delay.
        Respects daily message limits.
        """
        if not account.can_send_message():
            logger.warning("Daily limit reached for account %s", account.phone_number)
            return False

        if account.status != TelegramAccount.Status.ACTIVE:
            logger.warning("Account %s is not active", account.phone_number)
            return False

        async def _send():
            from telethon import TelegramClient
            from telethon.sessions import StringSession

            client = TelegramClient(
                StringSession(account.session_string),
                __import__("django.conf", fromlist=["settings"]).settings.TELEGRAM_API_ID,
                __import__("django.conf", fromlist=["settings"]).settings.TELEGRAM_API_HASH,
            )
            await client.connect()

            # Human-like delay
            delay = random.uniform(account.ai_delay_min, account.ai_delay_max)
            await asyncio.sleep(delay)

            # Simulate typing
            async with client.action(chat_id, "typing"):
                await asyncio.sleep(min(len(text) / 50, 5))  # typing duration

            await client.send_message(chat_id, text)
            await client.disconnect()

        try:
            asyncio.run(_send())
            account.messages_sent_today += 1
            account.save(update_fields=["messages_sent_today"])

            TelegramMessage.objects.create(
                account=account,
                organization=account.organization,
                telegram_message_id=0,
                sender_id=account.telegram_user_id or 0,
                sender_username=account.username,
                sender_name=account.first_name,
                chat_id=chat_id,
                text=text,
                direction=TelegramMessage.Direction.OUTBOUND,
                ai_processed=True,
            )
            return True
        except Exception as e:
            logger.error("send_message error [%s → %s]: %s", account.phone_number, chat_id, e)
            return False

    @staticmethod
    def log_inbound(account: TelegramAccount, event_data: dict) -> "TelegramMessage":
        """Log an inbound Telegram message to the database."""
        return TelegramMessage.objects.create(
            account=account,
            organization=account.organization,
            telegram_message_id=event_data.get("message_id", 0),
            sender_id=event_data.get("sender_id", 0),
            sender_username=event_data.get("username", ""),
            sender_name=event_data.get("name", ""),
            chat_id=event_data.get("chat_id", 0),
            text=event_data.get("text", ""),
            direction=TelegramMessage.Direction.INBOUND,
        )
