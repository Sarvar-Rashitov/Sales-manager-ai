from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.analytics.services import AnalyticsService
from apps.crm.models import Lead
from apps.followups.models import FollowUp


@login_required
def index(request):
    if not request.user.organization:
        return redirect("accounts:profile")

    org = request.user.organization
    stats = AnalyticsService.get_dashboard_stats(org)
    recent_leads = Lead.objects.filter(organization=org).order_by("-created_at")[:5]
    upcoming_followups = FollowUp.objects.filter(
        organization=org, status=FollowUp.Status.PENDING
    ).order_by("scheduled_at")[:5]

    return render(request, "dashboard/index.html", {
        "stats": stats,
        "recent_leads": recent_leads,
        "upcoming_followups": upcoming_followups,
    })
