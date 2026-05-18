from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.crm.models import Lead
from .models import Proposal
from apps.ai_agents.services.proposal_agent import ProposalAgent


@login_required
def proposal_list(request):
    proposals = Proposal.objects.filter(organization=request.user.organization)
    return render(request, "sales/proposal_list.html", {"proposals": proposals})


@login_required
def proposal_detail(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk, organization=request.user.organization)
    return render(request, "sales/proposal_detail.html", {"proposal": proposal})


@login_required
def generate_proposal(request, lead_pk):
    lead = get_object_or_404(Lead, pk=lead_pk, organization=request.user.organization)
    agent = ProposalAgent(lead)
    content = agent.generate_proposal()

    proposal = Proposal.objects.create(
        organization=request.user.organization,
        lead=lead,
        created_by=request.user,
        title=f"Proposal for {lead.title}",
        content=content,
    )
    messages.success(request, "AI proposal generated.")
    return redirect("sales:proposal_detail", pk=proposal.pk)
