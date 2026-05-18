"""
Knowledge base models - documents and embeddings for RAG.
"""
from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import User, Organization


class Document(BaseModel):
    class DocType(models.TextChoices):
        PDF = "pdf", "PDF"
        DOCX = "docx", "DOCX"
        TXT = "txt", "Text"
        URL = "url", "Website URL"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="documents")
    title = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=10, choices=DocType.choices)
    file = models.FileField(upload_to="knowledge_base/", blank=True, null=True)
    url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    chunk_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = "documents"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class DocumentChunk(BaseModel):
    """A single text chunk from a document, with its embedding stored in FAISS."""

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    chunk_index = models.PositiveIntegerField()
    text = models.TextField()
    faiss_id = models.BigIntegerField(null=True, blank=True, help_text="Index in FAISS vector store")

    class Meta:
        db_table = "document_chunks"
        ordering = ["document", "chunk_index"]

    def __str__(self):
        return f"{self.document.title} - chunk {self.chunk_index}"
