"""
Auth va Settings formlari.
"""
from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User, OrganizationSettings


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    org_name = forms.CharField(max_length=255, label="Company / Organization Name")
    password = forms.CharField(widget=forms.PasswordInput, validators=[validate_password])
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("password_confirm"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()


class PasswordResetForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, validators=[validate_password])
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("password_confirm"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


class InviteForm(forms.Form):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=User.Role.choices)


class AcceptInviteForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, validators=[validate_password])
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("password_confirm"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


class OrganizationSettingsForm(forms.ModelForm):
    """Kompaniya sozlamalari formasi — dashboard'dan to'ldiriladi."""

    # Parol maydonlari — ko'rsatilmaydi, faqat yangi kiritilsa saqlanadi
    openai_api_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=True),
        label="OpenAI API Key",
        help_text="Bo'sh qoldirsangiz global .env kaliti ishlatiladi",
    )
    telegram_api_hash = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=True),
        label="Telegram API Hash",
    )

    class Meta:
        model = OrganizationSettings
        fields = [
            # OpenAI
            "openai_api_key", "openai_model", "openai_embedding_model",
            # Telegram MTProto
            "telegram_api_id", "telegram_api_hash",
            # AI behaviour
            "ai_enabled", "ai_reply_delay_min", "ai_reply_delay_max",
            "daily_message_limit", "ai_language",
            # Notifications
            "notify_email", "notify_on_new_lead", "notify_on_qualified_lead",
            # Branding / AI context
            "company_description", "products_services", "support_contact",
        ]
        widgets = {
            "company_description": forms.Textarea(attrs={"rows": 4}),
            "products_services": forms.Textarea(attrs={"rows": 4}),
            "openai_model": forms.TextInput(attrs={"placeholder": "gpt-4o-mini"}),
        }
        labels = {
            "ai_enabled": "AI avtomatik javob yoqilgan",
            "notify_on_new_lead": "Yangi lead kelganda xabardor qil",
            "notify_on_qualified_lead": "Lead qualified bo'lganda xabardor qil",
        }
