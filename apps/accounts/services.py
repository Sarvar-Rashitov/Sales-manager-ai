"""
Accounts service layer — all business logic lives here, not in views.
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils.text import slugify

from apps.common.utils import generate_token
from .models import User, Organization, TeamInvite

logger = logging.getLogger("apps.accounts")


class AuthService:
    """Handles registration, login, email verification, password reset."""

    @staticmethod
    def register(email: str, password: str, first_name: str = "", last_name: str = "",
                 org_name: str = "") -> User:
        """Create a new user and optionally a new organization."""
        if User.objects.filter(email=email).exists():
            raise ValueError("A user with this email already exists.")

        org = None
        if org_name:
            slug = slugify(org_name)
            # ensure unique slug
            base_slug = slug
            counter = 1
            while Organization.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            org = Organization.objects.create(name=org_name, slug=slug)

        token = generate_token(48)
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            organization=org,
            role=User.Role.OWNER if org else User.Role.OPERATOR,
            email_verification_token=token,
        )

        AuthService._send_verification_email(user)
        logger.info("New user registered: %s", email)
        return user

    @staticmethod
    def verify_email(token: str) -> bool:
        try:
            user = User.objects.get(email_verification_token=token)
            user.email_verified = True
            user.email_verification_token = ""
            user.save(update_fields=["email_verified", "email_verification_token"])
            return True
        except User.DoesNotExist:
            return False

    @staticmethod
    def request_password_reset(email: str) -> None:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return  # silent — don't reveal if email exists

        token = generate_token(48)
        user.password_reset_token = token
        user.save(update_fields=["password_reset_token"])
        AuthService._send_password_reset_email(user)

    @staticmethod
    def reset_password(token: str, new_password: str) -> bool:
        try:
            user = User.objects.get(password_reset_token=token)
            user.set_password(new_password)
            user.password_reset_token = ""
            user.save(update_fields=["password", "password_reset_token"])
            return True
        except User.DoesNotExist:
            return False

    @staticmethod
    def _send_verification_email(user: User) -> None:
        link = f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/accounts/verify/{user.email_verification_token}/"
        send_mail(
            subject="Verify your AI Sales Manager account",
            message=f"Click to verify: {link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

    @staticmethod
    def _send_password_reset_email(user: User) -> None:
        link = f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/accounts/reset/{user.password_reset_token}/"
        send_mail(
            subject="Reset your AI Sales Manager password",
            message=f"Click to reset: {link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )


class InviteService:
    """Handles team invitations."""

    @staticmethod
    def send_invite(invited_by: User, email: str, role: str) -> TeamInvite:
        org = invited_by.organization
        if not org:
            raise ValueError("User has no organization.")

        token = generate_token(48)
        invite, _ = TeamInvite.objects.update_or_create(
            organization=org,
            email=email,
            defaults={
                "invited_by": invited_by,
                "role": role,
                "token": token,
                "accepted": False,
                "expires_at": timezone.now() + timedelta(days=7),
            },
        )

        link = f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/accounts/invite/{token}/"
        send_mail(
            subject=f"You're invited to join {org.name} on AI Sales Manager",
            message=f"Accept your invitation: {link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )
        return invite

    @staticmethod
    def accept_invite(token: str, password: str, first_name: str = "", last_name: str = "") -> User:
        try:
            invite = TeamInvite.objects.select_related("organization").get(
                token=token, accepted=False
            )
        except TeamInvite.DoesNotExist:
            raise ValueError("Invalid or expired invitation.")

        if timezone.now() > invite.expires_at:
            raise ValueError("Invitation has expired.")

        user, created = User.objects.get_or_create(
            email=invite.email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "organization": invite.organization,
                "role": invite.role,
                "email_verified": True,
            },
        )
        if created:
            user.set_password(password)
            user.save()

        invite.accepted = True
        invite.save(update_fields=["accepted"])
        return user
