from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .models import Document
from .services.rag_service import RAGService
from .forms import DocumentUploadForm


@login_required
def document_list(request):
    docs = Document.objects.filter(organization=request.user.organization)
    return render(request, "knowledge_base/document_list.html", {"documents": docs})


@login_required
@require_http_methods(["GET", "POST"])
def document_upload(request):
    form = DocumentUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        doc = form.save(commit=False)
        doc.organization = request.user.organization
        doc.uploaded_by = request.user
        doc.save()

        # Process synchronously (no Celery)
        RAGService.ingest_document(doc)

        if doc.status == Document.Status.READY:
            messages.success(request, f"Document '{doc.title}' processed ({doc.chunk_count} chunks).")
        else:
            messages.error(request, f"Processing failed: {doc.error_message}")

        return redirect("knowledge_base:document_list")

    return render(request, "knowledge_base/document_upload.html", {"form": form})


@login_required
def document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk, organization=request.user.organization)
    doc.delete()
    messages.success(request, "Document deleted.")
    return redirect("knowledge_base:document_list")


@login_required
def search_view(request):
    query = request.GET.get("q", "")
    results = []
    if query:
        results = RAGService.search(request.user.organization, query)
    return render(request, "knowledge_base/search.html", {"query": query, "results": results})
