"""
Custom User model with organization support and role-based access.
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from apps.common.models import BaseModel


class Organization(BaseModel):
    """A company / team that owns the SaaS subscription."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to="org_logos/", blank=True, null=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "organizations"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def settings(self):
        """Shortcut: org.settings.openai_api_key"""
        return getattr(self, "org_settings", None)


class OrganizationSettings(BaseModel):
    """
    Per-company configuration - each company manages its own keys and settings
    from their dashboard. Sensitive fields are stored encrypted-at-rest in production
    (use environment-level encryption or django-fernet-fields).
    """

    organization = models.OneToOneField(
        Organization, on_delete=models.CASCADE, related_name="org_settings"
    )

    # --- OpenAI ---
    openai_api_key = models.CharField(max_length=200, blank=True, help_text="Company-specific OpenAI key (overrides global)")
    openai_model = models.CharField(max_length=100, blank=True, default="gpt-4o-mini")
    openai_embedding_model = models.CharField(max_length=100, blank=True, default="text-embedding-3-small")

    # --- Telegram MTProto (Userbot) ---
    telegram_api_id = models.CharField(max_length=20, blank=True, help_text="From my.telegram.org/apps")
    telegram_api_hash = models.CharField(max_length=64, blank=True)

    # --- Telegram Bot API ---
    telegram_bot_token = models.CharField(max_length=200, blank=True, help_text="From @BotFather")
    telegram_bot_username = models.CharField(max_length=100, blank=True)
    telegram_bot_webhook_secret = models.CharField(max_length=64, blank=True)

    # --- AI Behaviour ---
    ai_enabled = models.BooleanField(default=True)
    ai_reply_delay_min = models.PositiveIntegerField(default=2, help_text="Seconds")
    ai_reply_delay_max = models.PositiveIntegerField(default=8, help_text="Seconds")
    daily_message_limit = models.PositiveIntegerField(default=200)
    ai_language = models.CharField(max_length=10, default="auto", help_text="'auto' detects language, or set e.g. 'uz', 'ru', 'en'")

    # --- Notifications ---
    notify_email = models.EmailField(blank=True, help_text="Send alerts to this email")
    notify_on_new_lead = models.BooleanField(default=True)
    notify_on_qualified_lead = models.BooleanField(default=True)

    # --- Branding ---
    company_description = models.TextField(blank=True, help_text="Used in AI system prompts")
    products_services = models.TextField(blank=True, help_text="List of products/services for AI context")
    support_contact = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "organization_settings"

    def __str__(self):
        return f"Settings - {self.organization.name}"

    def get_openai_key(self) -> str:
        """Return company key if set, otherwise fall back to global .env key."""
        from django.conf import settings
        return self.openai_api_key or settings.OPENAI_API_KEY

    def get_openai_model(self) -> str:
        from django.conf import settings
        return self.openai_model or settings.OPENAI_MODEL

    def get_telegram_api_id(self) -> str:
        from django.conf import settings
        return self.telegram_api_id or settings.TELEGRAM_API_ID

    def get_telegram_api_hash(self) -> str:
        from django.conf import settings
        return self.telegram_api_hash or settings.TELEGRAM_API_HASH


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str = None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.OWNER)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Custom user model.
    - Email-based login
    - Belongs to an Organization
    - Has a Role
    """

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        SALES_MANAGER = "sales_manager", "Sales Manager"
        OPERATOR = "operator", "Operator"
        VIEWER = "viewer", "Viewer"

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.OPERATOR)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, blank=True)
    password_reset_token = models.CharField(max_length=64, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ["email"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["organization", "role"]),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def has_role(self, *roles) -> bool:
        return self.role in roles


class TeamInvite(BaseModel):
    """Pending invitation to join an organization."""

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="invites"
    )
    invited_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_invites"
    )
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=User.Role.choices, default=User.Role.OPERATOR)
    token = models.CharField(max_length=64, unique=True)
    accepted = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "team_invites"
        unique_together = [("organization", "email")]

    def __str__(self):
        return f"Invite {self.email} -> {self.organization}"
