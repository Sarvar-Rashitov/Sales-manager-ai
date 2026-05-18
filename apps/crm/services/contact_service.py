"""
Contact service — create and manage contacts.
"""
from apps.accounts.models import Organization
from ..models import Contact, Company


class ContactService:

    @staticmethod
    def create_contact(
        organization: Organization,
        first_name: str,
        last_name: str = "",
        email: str = "",
        phone: str = "",
        telegram_username: str = "",
        telegram_id: int = None,
        company: Company = None,
    ) -> Contact:
        return Contact.objects.create(
            organization=organization,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            telegram_username=telegram_username,
            telegram_id=telegram_id,
            company=company,
        )

    @staticmethod
    def find_by_telegram(organization: Organization, telegram_id: int) -> Contact | None:
        return Contact.objects.filter(
            organization=organization, telegram_id=telegram_id
        ).first()

    @staticmethod
    def get_contacts_for_org(organization: Organization):
        return Contact.objects.filter(organization=organization).select_related("company", "assigned_to")
