"""
Userbot service — runs the Telethon event loop for a Telegram account.
Handles incoming messages, routes to AI, sends responses.

This is designed to be run via Django management command (no Celery needed).
"""
import asyncio
import logging
from django.conf import settings
from ..models import TelegramAccount, TelegramMessage
from .message_service import MessageService

logger = logging.getLogger("apps.telegram_bot")


class UserbotService:

    def __init__(self, account: TelegramAccount):
        self.account = account
        self.client = None

    def _build_client(self):
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        return TelegramClient(
            StringSession(self.account.session_string),
            int(settings.TELEGRAM_API_ID),
            settings.TELEGRAM_API_HASH,
        )

    async def start(self):
        """Start the userbot event loop."""
        from telethon import events

        self.client = self._build_client()
        await self.client.connect()

        if not await self.client.is_user_authorized():
            logger.error("Account %s is not authorized", self.account.phone_number)
            return

        logger.info("Userbot started for %s", self.account.phone_number)

        @self.client.on(events.NewMessage(incoming=True))
        async def handle_message(event):
            await self._process_message(event)

        await self.client.run_until_disconnected()

    async def _process_message(self, event):
        """Process an incoming Telegram message through the AI pipeline."""
        try:
            sender = await event.get_sender()
            if not sender or getattr(sender, "bot", False):
                return  # ignore bots

            sender_id = sender.id
            username = getattr(sender, "username", "") or ""
            first_name = getattr(sender, "first_name", "") or ""
            text = event.message.text or ""

            if not text:
                return

            # Log inbound message
            MessageService.log_inbound(self.account, {
                "message_id": event.message.id,
                "sender_id": sender_id,
                "username": username,
                "name": first_name,
                "chat_id": event.chat_id,
                "text": text,
            })

            if not self.account.is_ai_enabled:
                return

            # Get or create lead in CRM
            from apps.crm.services.lead_service import LeadService
            lead, _ = LeadService.get_or_create_lead_from_telegram(
                organization=self.account.organization,
                telegram_id=sender_id,
                username=username,
                first_name=first_name,
            )

            # Route through AI agent
            from apps.ai_agents.services.agent_router import AgentRouter
            response = AgentRouter.route(lead, text)

            if response:
                # Send response (with human-like delay handled inside)
                MessageService.send_message(self.account, event.chat_id, response)

        except Exception as e:
            logger.error("Error processing Telegram message: %s", e, exc_info=True)

    def run(self):
        """Synchronous entry point — called from management command."""
        asyncio.run(self.start())
