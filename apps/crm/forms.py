from django import forms
from .models import Lead, Contact, Company, Deal, Task, Note, PipelineStage


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["title", "status", "source", "budget", "notes", "assigned_to"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["first_name", "last_name", "email", "phone", "telegram_username", "company", "position", "notes"]


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "website", "industry", "size", "country", "notes"]


class DealForm(forms.ModelForm):
    def __init__(self, *args, org=None, **kwargs):
        super().__init__(*args, **kwargs)
        if org:
            self.fields["pipeline_stage"].queryset = PipelineStage.objects.filter(
                pipeline__organization=org
            )

    class Meta:
        model = Deal
        fields = ["title", "value", "status", "pipeline_stage", "expected_close_date", "notes", "assigned_to"]
        widgets = {
            "expected_close_date": forms.DateInput(attrs={"type": "date"}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "priority", "due_date", "assigned_to"]
        widgets = {
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3, "placeholder": "Add a note..."}),
        }
