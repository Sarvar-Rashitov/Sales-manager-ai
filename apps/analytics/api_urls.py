from django.urls import path
from . import api_views

urlpatterns = [
    path("stats/", api_views.stats_api, name="api_stats"),
    path("funnel/", api_views.funnel_api, name="api_funnel"),
]
