from django import forms
from .models import Document


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "doc_type", "file", "url"]

    def clean(self):
        cleaned = super().clean()
        doc_type = cleaned.get("doc_type")
        file = cleaned.get("file")
        url = cleaned.get("url")

        if doc_type == Document.DocType.URL and not url:
            raise forms.ValidationError("URL is required for website documents.")
        if doc_type != Document.DocType.URL and not file:
            raise forms.ValidationError("File is required for this document type.")
        return cleaned
