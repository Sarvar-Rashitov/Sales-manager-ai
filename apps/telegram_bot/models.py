"""
Telegram models:
- TelegramAccount   — Userbot (MTProto / Telethon)
- TelegramBot       — Bot API (webhook)
- TelegramMessage   — Barcha xabarlar logi
- Broadcast         — Ommaviy xabar yuborish
- BroadcastRecipient— Har bir qabul qiluvchi holati
"""
from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import User, Organization


# ─────────────────────────────────────────────
# USERBOT (MTProto / Telethon)
# ─────────────────────────────────────────────

class TelegramAccount(BaseModel):
    """Real Telegram account — Telethon MTProto orqali boshqariladi."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Login"
        ACTIVE = "active", "Active"
        DISCONNECTED = "disconnected", "Disconnected"
        BANNED = "banned", "Banned"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="telegram_accounts")
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="telegram_accounts")

    phone_number = models.CharField(max_length=20, unique=True)
    session_string = models.TextField(blank=True, help_text="Telethon StringSession")
    telegram_user_id = models.BigIntegerField(null=True, blank=True)
    username = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    is_ai_enabled = models.BooleanField(default=True)
    ai_delay_min = models.PositiveIntegerField(default=2)
    ai_delay_max = models.PositiveIntegerField(default=8)
    daily_message_limit = models.PositiveIntegerField(default=50)
    messages_sent_today = models.PositiveIntegerField(default=0)
    last_reset_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "telegram_accounts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.phone_number} ({self.username or 'no username'})"

    def can_send_message(self) -> bool:
        from django.utils import timezone
        today = timezone.now().date()
        if self.last_reset_date != today:
            self.messages_sent_today = 0
            self.last_reset_date = today
            self.save(update_fields=["messages_sent_today", "last_reset_date"])
        return self.messages_sent_today < self.daily_message_limit


class TelegramSession(BaseModel):
    """OTP/2FA holati — login jarayonida."""

    account = models.OneToOneField(TelegramAccount, on_delete=models.CASCADE, related_name="session_state")
    phone_code_hash = models.CharField(max_length=100, blank=True)
    awaiting_code = models.BooleanField(default=False)
    awaiting_2fa = models.BooleanField(default=False)

    class Meta:
        db_table = "telegram_sessions"


# ─────────────────────────────────────────────
# BOT API (Webhook)
# ─────────────────────────────────────────────

class TelegramBot(BaseModel):
    """
    Telegram Bot API orqali ishlaydigan bot.
    Har bir kompaniya o'z botini qo'shadi (@BotFather token).
    Webhook: /telegram/bot/<uuid:pk>/webhook/
    """

    class Status(models.TextChoices):
        INACTIVE = "inactive", "Inactive"
        ACTIVE = "active", "Active"
        ERROR = "error", "Error"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="telegram_bots")
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="telegram_bots")

    name = models.CharField(max_length=150, help_text="Bot nomi (eslatma uchun)")
    bot_token = models.CharField(max_length=200, unique=True, help_text="@BotFather dan olingan token")
    bot_username = models.CharField(max_length=100, blank=True)
    bot_id = models.BigIntegerField(null=True, blank=True)
    webhook_secret = models.CharField(max_length=64, blank=True, help_text="Webhook xavfsizlik kaliti")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INACTIVE)
    is_ai_enabled = models.BooleanField(default=True)
    ai_delay_min = models.PositiveIntegerField(default=1)
    ai_delay_max = models.PositiveIntegerField(default=5)
    daily_message_limit = models.PositiveIntegerField(default=500)
    messages_sent_today = models.PositiveIntegerField(default=0)
    last_reset_date = models.DateField(null=True, blank=True)
    last_error = models.TextField(blank=True)

    class Meta:
        db_table = "telegram_bots"
        ordering = ["-created_at"]

    def __str__(self):
        return f"@{self.bot_username or self.name} [{self.organization.name}]"

    def can_send_message(self) -> bool:
        from django.utils import timezone
        today = timezone.now().date()
        if self.last_reset_date != today:
            self.messages_sent_today = 0
            self.last_reset_date = today
            self.save(update_fields=["messages_sent_today", "last_reset_date"])
        return self.messages_sent_today < self.daily_message_limit


# ─────────────────────────────────────────────
# XABARLAR LOGI
# ─────────────────────────────────────────────

class TelegramMessage(BaseModel):
    """Barcha Telegram xabarlari (userbot + bot) logi."""

    class Direction(models.TextChoices):
        INBOUND = "inbound", "Inbound"
        OUTBOUND = "outbound", "Outbound"

    class Source(models.TextChoices):
        USERBOT = "userbot", "Userbot"
        BOT = "bot", "Bot API"

    # Userbot yoki Bot — biri bo'ladi
    account = models.ForeignKey(
        TelegramAccount, on_delete=models.CASCADE,
        related_name="messages", null=True, blank=True
    )
    bot = models.ForeignKey(
        TelegramBot, on_delete=models.CASCADE,
        related_name="messages", null=True, blank=True
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="telegram_messages")

    source = models.CharField(max_length=10, choices=Source.choices, default=Source.USERBOT)
    telegram_message_id = models.BigIntegerField(default=0)
    sender_id = models.BigIntegerField()
    sender_username = models.CharField(max_length=100, blank=True)
    sender_name = models.CharField(max_length=200, blank=True)
    chat_id = models.BigIntegerField()
    text = models.TextField()
    direction = models.CharField(max_length=10, choices=Direction.choices)
    ai_processed = models.BooleanField(default=False)
    ai_response = models.TextField(blank=True)

    class Meta:
        db_table = "telegram_messages"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sender_id", "organization"]),
            models.Index(fields=["organization", "direction"]),
        ]

    def __str__(self):
        return f"{self.direction} | {self.sender_name} | {self.text[:50]}"


# ─────────────────────────────────────────────
# BROADCAST — Ommaviy xabar
# ─────────────────────────────────────────────

class Broadcast(BaseModel):
    """
    Ommaviy xabar yuborish kampaniyasi.
    Userbot yoki Bot API orqali yuboriladi.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    class Channel(models.TextChoices):
        USERBOT = "userbot", "Userbot (MTProto)"
        BOT = "bot", "Bot API"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="broadcasts")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="broadcasts")

    # Qaysi kanal orqali yuboriladi
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.BOT)
    userbot_account = models.ForeignKey(
        TelegramAccount, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="broadcasts",
        help_text="Userbot tanlanganda"
    )
    bot = models.ForeignKey(
        TelegramBot, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="broadcasts",
        help_text="Bot API tanlanganda"
    )

    name = models.CharField(max_length=255)
    message_text = models.TextField(help_text="Yuborilajak xabar matni. {name} o'zgaruvchisi qo'llaniladi.")
    parse_mode = models.CharField(
        max_length=10, default="HTML",
        choices=[("HTML", "HTML"), ("Markdown", "Markdown"), ("plain", "Plain Text")]
    )

    # Kimga yuboriladi
    target_all_leads = models.BooleanField(default=False, help_text="Barcha leadlarga yuborish")
    target_leads = models.ManyToManyField(
        "crm.Lead", blank=True, related_name="broadcasts",
        help_text="Aniq leadlar tanlanganda"
    )

    # Holat
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_recipients = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = "broadcasts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} [{self.status}]"

    @property
    def success_rate(self) -> float:
        if self.total_recipients == 0:
            return 0.0
        return round(self.sent_count / self.total_recipients * 100, 1)


class BroadcastRecipient(BaseModel):
    """Har bir qabul qiluvchining yuborish holati."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped (no Telegram ID)"

    broadcast = models.ForeignKey(Broadcast, on_delete=models.CASCADE, related_name="recipients")
    lead = models.ForeignKey("crm.Lead", on_delete=models.CASCADE, related_name="broadcast_recipients")
    telegram_id = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    personalized_message = models.TextField(blank=True)

    class Meta:
        db_table = "broadcast_recipients"
        unique_together = [("broadcast", "lead")]
