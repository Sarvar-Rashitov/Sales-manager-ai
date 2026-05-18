"""
Django Channels WebSocket consumer for real-time chat.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger("apps.messaging")


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for a single conversation.
    Room group: conversation_{conversation_id}
    """

    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"conversation_{self.conversation_id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info("WebSocket connected: %s", self.room_group_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming WebSocket message from browser."""
        data = json.loads(text_data)
        message_type = data.get("type", "message")

        if message_type == "message":
            content = data.get("content", "").strip()
            if not content:
                return

            # Save message to DB
            message = await self._save_message(content)

            # Broadcast to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "content": content,
                    "sender_type": "operator",
                    "message_id": str(message.id),
                    "timestamp": message.created_at.isoformat(),
                },
            )

        elif message_type == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "typing_indicator", "is_typing": data.get("is_typing", False)},
            )

    async def chat_message(self, event):
        """Send message to WebSocket client."""
        await self.send(text_data=json.dumps({
            "type": "message",
            "content": event["content"],
            "sender_type": event["sender_type"],
            "message_id": event["message_id"],
            "timestamp": event["timestamp"],
        }))

    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "is_typing": event["is_typing"],
        }))

    @database_sync_to_async
    def _save_message(self, content: str):
        from .models import Conversation, Message
        conversation = Conversation.objects.get(id=self.conversation_id)
        return Message.objects.create(
            conversation=conversation,
            sender_type=Message.SenderType.OPERATOR,
            sender=self.scope.get("user"),
            content=content,
        )
