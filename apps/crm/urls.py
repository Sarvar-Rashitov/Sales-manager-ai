from django.urls import path
from . import views

app_name = "crm"

urlpatterns = [
    # Leads
    path("leads/", views.lead_list, name="lead_list"),
    path("leads/create/", views.lead_create, name="lead_create"),
    path("leads/<uuid:pk>/", views.lead_detail, name="lead_detail"),
    path("leads/<uuid:pk>/edit/", views.lead_edit, name="lead_edit"),
    path("leads/<uuid:pk>/status/", views.update_lead_status, name="lead_status"),
    path("leads/<uuid:lead_pk>/notes/", views.add_note, name="add_note"),

    # Contacts
    path("contacts/", views.contact_list, name="contact_list"),
    path("contacts/create/", views.contact_create, name="contact_create"),
    path("contacts/<uuid:pk>/", views.contact_detail, name="contact_detail"),

    # Companies
    path("companies/", views.company_list, name="company_list"),
    path("companies/create/", views.company_create, name="company_create"),

    # Deals
    path("deals/", views.deal_list, name="deal_list"),
    path("deals/create/", views.deal_create, name="deal_create"),

    # Tasks
    path("tasks/", views.task_list, name="task_list"),
]
