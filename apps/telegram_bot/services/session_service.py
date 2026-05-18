"""
Telegram session management using Telethon StringSession.
Handles login flow: send code → verify code → 2FA.
"""
import logging
import asyncio
from django.conf import settings
from ..models import TelegramAccount, TelegramSession

logger = logging.getLogger("apps.telegram_bot")


def _get_client(session_string: str = ""):
    """Create a Telethon TelegramClient."""
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        return TelegramClient(
            StringSession(session_string),
            int(settings.TELEGRAM_API_ID),
            settings.TELEGRAM_API_HASH,
        )
    except ImportError:
        raise RuntimeError("Telethon is not installed. Run: pip install telethon")


class SessionService:

    @staticmethod
    def send_code(account: TelegramAccount) -> bool:
        """Send OTP code to the phone number. Returns True on success."""
        async def _send():
            client = _get_client()
            await client.connect()
            result = await client.send_code_request(account.phone_number)
            session_state, _ = TelegramSession.objects.get_or_create(account=account)
            session_state.phone_code_hash = result.phone_code_hash
            session_state.awaiting_code = True
            session_state.save()
            await client.disconnect()
            return True

        try:
            return asyncio.run(_send())
        except Exception as e:
            logger.error("send_code error for %s: %s", account.phone_number, e)
            return False

    @staticmethod
    def verify_code(account: TelegramAccount, code: str) -> dict:
        """
        Verify OTP code. Returns {'success': bool, 'needs_2fa': bool}.
        On success, saves StringSession to account.
        """
        async def _verify():
            from telethon.errors import SessionPasswordNeededError
            from telethon.sessions import StringSession

            session_state = TelegramSession.objects.get(account=account)
            client = _get_client()
            await client.connect()

            try:
                await client.sign_in(
                    phone=account.phone_number,
                    code=code,
                    phone_code_hash=session_state.phone_code_hash,
                )
                me = await client.get_me()
                session_string = client.session.save()
                await client.disconnect()

                account.session_string = session_string
                account.telegram_user_id = me.id
                account.username = me.username or ""
                account.first_name = me.first_name or ""
                account.status = TelegramAccount.Status.ACTIVE
                account.save()

                session_state.awaiting_code = False
                session_state.save()

                return {"success": True, "needs_2fa": False}

            except SessionPasswordNeededError:
                session_state.awaiting_2fa = True
                session_state.awaiting_code = False
                session_state.save()
                await client.disconnect()
                return {"success": False, "needs_2fa": True}

        try:
            return asyncio.run(_verify())
        except Exception as e:
            logger.error("verify_code error: %s", e)
            return {"success": False, "needs_2fa": False, "error": str(e)}

    @staticmethod
    def verify_2fa(account: TelegramAccount, password: str) -> bool:
        """Verify 2FA password and save session."""
        async def _verify():
            from telethon.sessions import StringSession
            client = _get_client()
            await client.connect()
            await client.sign_in(password=password)
            me = await client.get_me()
            session_string = client.session.save()
            await client.disconnect()

            account.session_string = session_string
            account.telegram_user_id = me.id
            account.username = me.username or ""
            account.first_name = me.first_name or ""
            account.status = TelegramAccount.Status.ACTIVE
            account.save()
            return True

        try:
            return asyncio.run(_verify())
        except Exception as e:
            logger.error("verify_2fa error: %s", e)
            return False

    @staticmethod
    def disconnect(account: TelegramAccount) -> None:
        account.status = TelegramAccount.Status.DISCONNECTED
        account.session_string = ""
        account.save(update_fields=["status", "session_string"])
