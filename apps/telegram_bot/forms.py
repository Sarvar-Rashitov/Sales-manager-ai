from django import forms
from .models import TelegramAccount, TelegramBot, Broadcast


class TelegramAccountForm(forms.ModelForm):
    class Meta:
        model = TelegramAccount
        fields = ["phone_number", "is_ai_enabled", "ai_delay_min", "ai_delay_max", "daily_message_limit"]
        widgets = {
            "phone_number": forms.TextInput(attrs={"placeholder": "+998901234567"}),
        }


class VerifyCodeForm(forms.Form):
    code = forms.CharField(max_length=10, label="Telegram OTP Code",
                           widget=forms.TextInput(attrs={"placeholder": "12345", "autofocus": True}))


class Verify2FAForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label="2FA Password")


class TelegramBotForm(forms.ModelForm):
    class Meta:
        model = TelegramBot
        fields = ["name", "bot_token", "is_ai_enabled", "ai_delay_min", "ai_delay_max", "daily_message_limit"]
        widgets = {
            "bot_token": forms.PasswordInput(render_value=True,
                                             attrs={"placeholder": "1234567890:ABCdef..."}),
        }
        help_texts = {
            "bot_token": "@BotFather dan olingan token",
            "name": "Eslatma uchun nom (masalan: Sales Bot)",
        }


class BroadcastForm(forms.ModelForm):
    def __init__(self, *args, org=None, **kwargs):
        super().__init__(*args, **kwargs)
        if org:
            self.fields["userbot_account"].queryset = TelegramAccount.objects.filter(
                organization=org, status="active"
            )
            self.fields["bot"].queryset = TelegramBot.objects.filter(
                organization=org, status="active"
            )
            from apps.crm.models import Lead
            self.fields["target_leads"].queryset = Lead.objects.filter(organization=org)

    class Meta:
        model = Broadcast
        fields = [
            "name", "channel", "userbot_account", "bot",
            "message_text", "parse_mode",
            "target_all_leads", "target_leads",
        ]
        widgets = {
            "message_text": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Salom {name}! Sizga maxsus taklif bor...",
            }),
            "target_leads": forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            "message_text": "{name} - qabul qiluvchi ismi bilan almashtiriladi",
            "target_all_leads": "Barcha leadlarga yuborish (quyidagi tanlovni bekor qiladi)",
        }
