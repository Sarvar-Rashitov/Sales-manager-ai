"""
CRM views — leads, contacts, companies, deals, tasks.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Lead, Contact, Company, Deal, Task, Note, Pipeline
from .services.lead_service import LeadService
from .services.contact_service import ContactService
from .forms import LeadForm, ContactForm, CompanyForm, DealForm, TaskForm, NoteForm


@login_required
def lead_list(request):
    status_filter = request.GET.get("status", "")
    leads = LeadService.get_leads_for_org(request.user.organization, status=status_filter or None)
    return render(request, "crm/lead_list.html", {
        "leads": leads,
        "status_filter": status_filter,
        "status_choices": Lead.Status.choices,
    })


@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk, organization=request.user.organization)
    notes = Note.objects.filter(lead=lead)
    activities = lead.activities.order_by("-created_at")[:20]
    return render(request, "crm/lead_detail.html", {
        "lead": lead,
        "notes": notes,
        "activities": activities,
        "note_form": NoteForm(),
    })


@login_required
@require_http_methods(["GET", "POST"])
def lead_create(request):
    form = LeadForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        lead = LeadService.create_lead(
            organization=request.user.organization,
            title=form.cleaned_data["title"],
            source=form.cleaned_data["source"],
            notes=form.cleaned_data.get("notes", ""),
            assigned_to=request.user,
        )
        messages.success(request, "Lead created.")
        return redirect("crm:lead_detail", pk=lead.pk)
    return render(request, "crm/lead_form.html", {"form": form, "action": "Create"})


@login_required
@require_http_methods(["GET", "POST"])
def lead_edit(request, pk):
    lead = get_object_or_404(Lead, pk=pk, organization=request.user.organization)
    form = LeadForm(request.POST or None, instance=lead)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Lead updated.")
        return redirect("crm:lead_detail", pk=lead.pk)
    return render(request, "crm/lead_form.html", {"form": form, "action": "Edit", "lead": lead})


@login_required
def contact_list(request):
    contacts = ContactService.get_contacts_for_org(request.user.organization)
    return render(request, "crm/contact_list.html", {"contacts": contacts})


@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk, organization=request.user.organization)
    return render(request, "crm/contact_detail.html", {"contact": contact})


@login_required
@require_http_methods(["GET", "POST"])
def contact_create(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        contact = form.save(commit=False)
        contact.organization = request.user.organization
        contact.save()
        messages.success(request, "Contact created.")
        return redirect("crm:contact_detail", pk=contact.pk)
    return render(request, "crm/contact_form.html", {"form": form, "action": "Create"})


@login_required
def company_list(request):
    companies = Company.objects.filter(organization=request.user.organization)
    return render(request, "crm/company_list.html", {"companies": companies})


@login_required
@require_http_methods(["GET", "POST"])
def company_create(request):
    form = CompanyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        company = form.save(commit=False)
        company.organization = request.user.organization
        company.save()
        messages.success(request, "Company created.")
        return redirect("crm:company_list")
    return render(request, "crm/company_form.html", {"form": form, "action": "Create"})


@login_required
def deal_list(request):
    deals = Deal.objects.filter(organization=request.user.organization).select_related(
        "lead", "contact", "pipeline_stage", "assigned_to"
    )
    return render(request, "crm/deal_list.html", {"deals": deals})


@login_required
@require_http_methods(["GET", "POST"])
def deal_create(request):
    form = DealForm(request.POST or None, org=request.user.organization)
    if request.method == "POST" and form.is_valid():
        deal = form.save(commit=False)
        deal.organization = request.user.organization
        deal.save()
        messages.success(request, "Deal created.")
        return redirect("crm:deal_list")
    return render(request, "crm/deal_form.html", {"form": form, "action": "Create"})


@login_required
def task_list(request):
    tasks = Task.objects.filter(
        organization=request.user.organization, completed=False
    ).select_related("lead", "deal", "assigned_to")
    return render(request, "crm/task_list.html", {"tasks": tasks})


@login_required
@require_http_methods(["POST"])
def add_note(request, lead_pk):
    lead = get_object_or_404(Lead, pk=lead_pk, organization=request.user.organization)
    form = NoteForm(request.POST)
    if form.is_valid():
        note = form.save(commit=False)
        note.organization = request.user.organization
        note.author = request.user
        note.lead = lead
        note.save()
    return redirect("crm:lead_detail", pk=lead_pk)


@login_required
@require_http_methods(["POST"])
def update_lead_status(request, pk):
    """HTMX endpoint to update lead status inline."""
    lead = get_object_or_404(Lead, pk=pk, organization=request.user.organization)
    new_status = request.POST.get("status")
    if new_status in dict(Lead.Status.choices):
        LeadService.update_status(lead, new_status, user=request.user)
    return JsonResponse({"status": lead.status, "status_display": lead.get_status_display()})
