from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from apps.crm.models import Lead
from .models import FollowUp
from .services import FollowUpService
from .forms import FollowUpForm


@login_required
def followup_list(request):
    followups = FollowUp.objects.filter(
        organization=request.user.organization
    ).select_related("lead", "assigned_to")
    return render(request, "followups/followup_list.html", {"followups": followups})


@login_required
@require_http_methods(["GET", "POST"])
def followup_create(request):
    form = FollowUpForm(request.POST or None, org=request.user.organization)
    if request.method == "POST" and form.is_valid():
        followup = form.save(commit=False)
        followup.organization = request.user.organization
        followup.assigned_to = request.user
        followup.save()
        messages.success(request, "Follow-up scheduled.")
        return redirect("followups:followup_list")
    return render(request, "followups/followup_form.html", {"form": form})


@login_required
def generate_ai_followup(request, lead_pk):
    lead = get_object_or_404(Lead, pk=lead_pk, organization=request.user.organization)
    followup = FollowUpService.generate_ai_followup(lead)
    messages.success(request, f"AI follow-up scheduled for {followup.scheduled_at:%Y-%m-%d %H:%M}.")
    return redirect("crm:lead_detail", pk=lead_pk)
