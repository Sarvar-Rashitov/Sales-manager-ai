from django.urls import path
from . import api_views

urlpatterns = [
    path("proposals/", api_views.proposal_list_api, name="api_proposals"),
]
