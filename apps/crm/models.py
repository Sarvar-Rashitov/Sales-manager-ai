"""
CRM models: Company, Contact, Lead, Pipeline, Deal, Task, Note, Activity.
"""
from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import User, Organization


class Company(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="companies")
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "companies"
        ordering = ["name"]
        indexes = [models.Index(fields=["organization", "name"])]

    def __str__(self):
        return self.name


class Contact(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="contacts")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="contacts")
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    telegram_username = models.CharField(max_length=100, blank=True)
    telegram_id = models.BigIntegerField(null=True, blank=True)
    position = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="contacts")

    class Meta:
        db_table = "contacts"
        ordering = ["first_name", "last_name"]
        indexes = [
            models.Index(fields=["organization", "email"]),
            models.Index(fields=["telegram_id"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Pipeline(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="pipelines")
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "pipelines"

    def __str__(self):
        return self.name


class PipelineStage(BaseModel):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name="stages")
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    probability = models.PositiveIntegerField(default=0, help_text="Win probability %")

    class Meta:
        db_table = "pipeline_stages"
        ordering = ["order"]

    def __str__(self):
        return f"{self.pipeline.name} -> {self.name}"


class Lead(BaseModel):
    class Status(models.TextChoices):
        NEW = "new", "New Lead"
        CONTACTED = "contacted", "Contacted"
        QUALIFIED = "qualified", "Qualified"
        DEMO = "demo", "Demo"
        NEGOTIATION = "negotiation", "Negotiation"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    class Source(models.TextChoices):
        TELEGRAM = "telegram", "Telegram"
        WEBSITE = "website", "Website"
        MANUAL = "manual", "Manual"
        REFERRAL = "referral", "Referral"
        OUTREACH = "outreach", "Outreach"
        OTHER = "other", "Other"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="leads")
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads")

    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.MANUAL)
    score = models.PositiveIntegerField(default=0, help_text="AI-generated lead score 0-100")
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    ai_summary = models.TextField(blank=True, help_text="AI-generated conversation summary")
    interests = models.JSONField(default=list, blank=True)
    last_contacted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "leads"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "assigned_to"]),
        ]

    def __str__(self):
        return self.title


class Deal(BaseModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        WON = "won", "Won"
        LOST = "lost", "Lost"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="deals")
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals")
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals")
    pipeline_stage = models.ForeignKey(PipelineStage, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals")

    title = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    expected_close_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "deals"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Task(BaseModel):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="tasks")
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tasks"
        ordering = ["due_date", "-priority"]

    def __str__(self):
        return self.title


class Note(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="crm_notes")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="crm_notes")
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name="crm_notes")
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="crm_notes")
    deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, null=True, blank=True, related_name="crm_notes")
    content = models.TextField()

    class Meta:
        db_table = "notes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note by {self.author} on {self.created_at:%Y-%m-%d}"


class Activity(BaseModel):
    class ActivityType(models.TextChoices):
        CALL = "call", "Call"
        EMAIL = "email", "Email"
        MEETING = "meeting", "Meeting"
        TELEGRAM = "telegram", "Telegram"
        NOTE = "note", "Note"
        STATUS_CHANGE = "status_change", "Status Change"
        AI_ACTION = "ai_action", "AI Action"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="activities")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")

    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "activities"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.activity_type} - {self.created_at:%Y-%m-%d %H:%M}"
