from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Document
from .services.rag_service import RAGService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_api(request):
    query = request.query_params.get("q", "")
    if not query:
        return Response({"results": []})
    results = RAGService.search(request.user.organization, query)
    return Response({"results": results})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def document_list_api(request):
    docs = Document.objects.filter(organization=request.user.organization).values(
        "id", "title", "doc_type", "status", "chunk_count", "created_at"
    )
    return Response(list(docs))
