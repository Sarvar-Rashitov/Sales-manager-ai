from django.urls import path
from . import views

app_name = "sales"

urlpatterns = [
    path("proposals/", views.proposal_list, name="proposal_list"),
    path("proposals/<uuid:pk>/", views.proposal_detail, name="proposal_detail"),
    path("proposals/generate/<uuid:lead_pk>/", views.generate_proposal, name="generate_proposal"),
]
