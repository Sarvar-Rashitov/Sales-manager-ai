from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.crm.models import Lead
from .services.agent_router import AgentRouter
from .services.proposal_agent import ProposalAgent
from .models import AILog
from .serializers import AILogSerializer, PromptSerializer
from . import models


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat_api(request, lead_pk):
    lead = get_object_or_404(Lead, pk=lead_pk, organization=request.user.organization)
    message = request.data.get("message", "").strip()
    if not message:
        return Response({"error": "message required"}, status=status.HTTP_400_BAD_REQUEST)
    response = AgentRouter.route(lead, message)
    return Response({"response": response})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def proposal_api(request, lead_pk):
    lead = get_object_or_404(Lead, pk=lead_pk, organization=request.user.organization)
    proposal = ProposalAgent(lead).generate_proposal()
    return Response({"proposal": proposal})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ai_logs_api(request):
    logs = AILog.objects.filter(organization=request.user.organization).order_by("-created_at")[:50]
    return Response(AILogSerializer(logs, many=True).data)
