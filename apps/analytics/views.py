import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .services import AnalyticsService


@login_required
def analytics_dashboard(request):
    org = request.user.organization
    stats = AnalyticsService.get_dashboard_stats(org)
    funnel = AnalyticsService.get_funnel_data(org)
    trend = AnalyticsService.get_lead_trend(org)
    sources = AnalyticsService.get_source_breakdown(org)

    return render(request, "analytics/dashboard.html", {
        "stats": stats,
        "funnel_json": json.dumps(funnel),
        "trend_json": json.dumps([
            {"date": str(d["date"]), "count": d["count"]} for d in trend
        ]),
        "sources_json": json.dumps(sources),
    })
