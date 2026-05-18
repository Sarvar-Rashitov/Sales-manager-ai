from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services import AnalyticsService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stats_api(request):
    return Response(AnalyticsService.get_dashboard_stats(request.user.organization))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def funnel_api(request):
    return Response(AnalyticsService.get_funnel_data(request.user.organization))
