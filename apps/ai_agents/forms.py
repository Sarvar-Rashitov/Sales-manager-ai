from django import forms
from .models import Prompt


class PromptForm(forms.ModelForm):
    class Meta:
        model = Prompt
        fields = ["name", "agent_type", "system_prompt", "is_active", "is_default"]
        widgets = {
            "system_prompt": forms.Textarea(attrs={"rows": 8}),
        }
