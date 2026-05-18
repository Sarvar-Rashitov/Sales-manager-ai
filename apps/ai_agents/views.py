"""
AI Agents views — chat interface, prompt management, AI logs.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from apps.crm.models import Lead
from .models import Prompt, AILog, ConversationMemory
from .services.agent_router import AgentRouter
from .services.proposal_agent import ProposalAgent
from .forms import PromptForm


@login_required
def chat_view(request, lead_pk):
    """Main AI chat interface for a lead."""
    lead = get_object_or_404(Lead, pk=lead_pk, organization=request.user.organization)
    memory, _ = ConversationMemory.objects.get_or_create(lead=lead)
    return render(request, "ai_agents/chat.html", {
        "lead": lead,
        "memory": memory,
        "messages": memory.messages,
    })


@login_required
@require_http_methods(["POST"])
def send_message(request, lead_pk):
    """HTMX endpoint — send a message and get AI response."""
    lead = get_object_or_404(Lead, pk=lead_pk, organization=request.user.organization)
    message = request.POST.get("message", "").strip()

    if not message:
        return JsonResponse({"error": "Empty message"}, status=400)

    response = AgentRouter.route(lead, message)

    if request.headers.get("HX-Request"):
        return render(request, "ai_agents/partials/message_pair.html", {
            "user_message": message,
            "ai_response": response,
        })

    return JsonResponse({"response": response})


@login_required
def generate_proposal(request, lead_pk):
    """Generate a sales proposal for a lead."""
    lead = get_object_or_404(Lead, pk=lead_pk, organization=request.user.organization)
    agent = ProposalAgent(lead)
    proposal = agent.generate_proposal()
    return render(request, "ai_agents/proposal.html", {
        "lead": lead,
        "proposal": proposal,
    })


@login_required
def prompt_list(request):
    prompts = Prompt.objects.filter(organization=request.user.organization)
    return render(request, "ai_agents/prompt_list.html", {"prompts": prompts})


@login_required
@require_http_methods(["GET", "POST"])
def prompt_create(request):
    form = PromptForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        prompt = form.save(commit=False)
        prompt.organization = request.user.organization
        prompt.save()
        return redirect("ai_agents:prompt_list")
    return render(request, "ai_agents/prompt_form.html", {"form": form, "action": "Create"})


@login_required
def ai_log_list(request):
    logs = AILog.objects.filter(organization=request.user.organization).order_by("-created_at")[:100]
    return render(request, "ai_agents/log_list.html", {"logs": logs})
