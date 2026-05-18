from django.contrib import admin
from .models import Document, DocumentChunk


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "doc_type", "status", "chunk_count", "organization", "created_at"]
    list_filter = ["doc_type", "status", "organization"]
    search_fields = ["title"]
    readonly_fields = ["status", "chunk_count", "error_message"]


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ["document", "chunk_index", "faiss_id"]
    list_filter = ["document"]
