"""
Telegram Bot API service.
- Webhook orqali kelgan update'larni qayta ishlaydi
- AI agent orqali javob beradi
- Xabar yuboradi (requests + Bot API)
"""
import logging
import time
import random
import requests as http_requests
from django.utils import timezone
from ..models import TelegramBot, TelegramMessage

logger = logging.getLogger("apps.telegram_bot")

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


class BotService:

    @staticmethod
    def send_message(bot: TelegramBot, chat_id: int, text: str,
                     parse_mode: str = "HTML") -> bool:
        """Bot API orqali xabar yuboradi."""
        if not bot.can_send_message():
            logger.warning("Daily limit reached for bot %s", bot.bot_username)
            return False

        # Human-like delay
        delay = random.uniform(bot.ai_delay_min, bot.ai_delay_max)
        time.sleep(delay)

        url = TELEGRAM_API.format(token=bot.bot_token, method="sendMessage")
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}

        try:
            resp = http_requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            bot.messages_sent_today += 1
            bot.save(update_fields=["messages_sent_today"])

            TelegramMessage.objects.create(
                bot=bot,
                organization=bot.organization,
                source=TelegramMessage.Source.BOT,
                sender_id=bot.bot_id or 0,
                sender_username=bot.bot_username,
                sender_name=bot.name,
                chat_id=chat_id,
                text=text,
                direction=TelegramMessage.Direction.OUTBOUND,
                ai_processed=True,
            )
            return True
        except Exception as e:
            logger.error("Bot send_message error [%s → %s]: %s", bot.bot_username, chat_id, e)
            bot.last_error = str(e)
            bot.save(update_fields=["last_error"])
            return False

    @staticmethod
    def set_webhook(bot: TelegramBot, webhook_url: str) -> dict:
        """Botga webhook URL o'rnatadi."""
        from apps.common.utils import generate_token
        if not bot.webhook_secret:
            bot.webhook_secret = generate_token(32)
            bot.save(update_fields=["webhook_secret"])

        url = TELEGRAM_API.format(token=bot.bot_token, method="setWebhook")
        payload = {
            "url": webhook_url,
            "secret_token": bot.webhook_secret,
            "allowed_updates": ["message", "callback_query"],
        }
        try:
            resp = http_requests.post(url, json=payload, timeout=10)
            data = resp.json()
            if data.get("ok"):
                bot.status = TelegramBot.Status.ACTIVE
                bot.save(update_fields=["status"])
            return data
        except Exception as e:
            logger.error("set_webhook error: %s", e)
            return {"ok": False, "description": str(e)}

    @staticmethod
    def delete_webhook(bot: TelegramBot) -> bool:
        url = TELEGRAM_API.format(token=bot.bot_token, method="deleteWebhook")
        try:
            http_requests.post(url, timeout=10)
            bot.status = TelegramBot.Status.INACTIVE
            bot.save(update_fields=["status"])
            return True
        except Exception as e:
            logger.error("delete_webhook error: %s", e)
            return False

    @staticmethod
    def get_bot_info(bot_token: str) -> dict:
        """Token to'g'riligini tekshiradi va bot ma'lumotlarini qaytaradi."""
        url = TELEGRAM_API.format(token=bot_token, method="getMe")
        try:
            resp = http_requests.get(url, timeout=10)
            return resp.json()
        except Exception as e:
            return {"ok": False, "description": str(e)}

    @staticmethod
    def process_webhook_update(bot: TelegramBot, update: dict) -> None:
        """
        Webhook'dan kelgan update'ni qayta ishlaydi.
        message → AI agent → javob yuboradi.
        """
        message = update.get("message") or update.get("edited_message")
        if not message:
            return

        text = message.get("text", "").strip()
        if not text:
            return

        chat = message.get("chat", {})
        sender = message.get("from", {})
        chat_id = chat.get("id")
        sender_id = sender.get("id")
        sender_username = sender.get("username", "")
        sender_name = f"{sender.get('first_name', '')} {sender.get('last_name', '')}".strip()

        # Xabarni logga yozamiz
        TelegramMessage.objects.create(
            bot=bot,
            organization=bot.organization,
            source=TelegramMessage.Source.BOT,
            telegram_message_id=message.get("message_id", 0),
            sender_id=sender_id,
            sender_username=sender_username,
            sender_name=sender_name,
            chat_id=chat_id,
            text=text,
            direction=TelegramMessage.Direction.INBOUND,
        )

        if not bot.is_ai_enabled:
            return

        # CRM: lead topamiz yoki yaratamiz
        try:
            from apps.crm.services.lead_service import LeadService
            lead, _ = LeadService.get_or_create_lead_from_telegram(
                organization=bot.organization,
                telegram_id=sender_id,
                username=sender_username,
                first_name=sender.get("first_name", ""),
            )

            # AI agent orqali javob
            from apps.ai_agents.services.agent_router import AgentRouter
            response = AgentRouter.route(lead, text)

            if response:
                BotService.send_message(bot, chat_id, response)

        except Exception as e:
            logger.error("process_webhook_update error: %s", e, exc_info=True)
