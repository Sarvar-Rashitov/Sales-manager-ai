from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Lead, Contact, Company, Deal, Task, Activity
from .serializers import (
    LeadSerializer, ContactSerializer, CompanySerializer,
    DealSerializer, TaskSerializer, ActivitySerializer,
)


class OrgFilterMixin:
    """Automatically filter querysets to the authenticated user's organization."""

    def get_queryset(self):
        return super().get_queryset().filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class LeadViewSet(OrgFilterMixin, viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    filterset_fields = ["status", "source", "assigned_to"]
    search_fields = ["title", "contact__first_name", "contact__last_name"]
    ordering_fields = ["created_at", "score", "status"]


class ContactViewSet(OrgFilterMixin, viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    search_fields = ["first_name", "last_name", "email", "telegram_username"]


class CompanyViewSet(OrgFilterMixin, viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    search_fields = ["name", "industry"]


class DealViewSet(OrgFilterMixin, viewsets.ModelViewSet):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    filterset_fields = ["status", "assigned_to"]


class TaskViewSet(OrgFilterMixin, viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_fields = ["completed", "priority", "assigned_to"]


class ActivityViewSet(OrgFilterMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    filterset_fields = ["activity_type", "lead", "contact"]
