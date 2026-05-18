from django import forms
from apps.crm.models import Lead
from .models import FollowUp


class FollowUpForm(forms.ModelForm):
    def __init__(self, *args, org=None, **kwargs):
        super().__init__(*args, **kwargs)
        if org:
            self.fields["lead"].queryset = Lead.objects.filter(organization=org)

    class Meta:
        model = FollowUp
        fields = ["lead", "message", "channel", "scheduled_at"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
            "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
