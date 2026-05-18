"""
AI Agent models: prompts, logs, memory, outreach campaigns.
"""
from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import User, Organization
from apps.crm.models import Lead, Contact


class Prompt(BaseModel):
    """Reusable system prompts for AI agents."""

    class AgentType(models.TextChoices):
        RECEPTION = "reception", "Reception Agent"
        QUALIFICATION = "qualification", "Qualification Agent"
        SALES = "sales", "Sales Conversation Agent"
        FOLLOWUP = "followup", "Follow-Up Agent"
        PROPOSAL = "proposal", "Proposal Generator"
        SENTIMENT = "sentiment", "Sentiment Analysis"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="prompts")
    name = models.CharField(max_length=255)
    agent_type = models.CharField(max_length=20, choices=AgentType.choices)
    system_prompt = models.TextField()
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "prompts"
        ordering = ["agent_type", "name"]

    def __str__(self):
        return f"{self.agent_type} - {self.name}"


class ConversationMemory(BaseModel):
    """Stores AI conversation context per lead."""

    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name="memory")
    messages = models.JSONField(default=list)  # list of {role, content} dicts
    summary = models.TextField(blank=True)
    detected_language = models.CharField(max_length=10, default="en")
    sentiment_score = models.FloatField(default=0.0)  # -1 to 1
    buying_intent_score = models.FloatField(default=0.0)  # 0 to 1
    extracted_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    extracted_interests = models.JSONField(default=list)
    last_agent = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = "conversation_memories"

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        # Keep last 50 messages to avoid token overflow
        if len(self.messages) > 50:
            self.messages = self.messages[-50:]
        self.save(update_fields=["messages", "updated_at"])

    def get_recent_messages(self, n: int = 10) -> list:
        return self.messages[-n:]


class AILog(BaseModel):
    """Audit log for every AI call."""

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="ai_logs")
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name="ai_logs")
    agent_type = models.CharField(max_length=20)
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    model = models.CharField(max_length=50)
    input_text = models.TextField(blank=True)
    output_text = models.TextField(blank=True)
    latency_ms = models.PositiveIntegerField(default=0)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = "ai_logs"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "agent_type", "created_at"])]


class OutreachCampaign(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="campaigns")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="campaigns")
    name = models.CharField(max_length=255)
    message_template = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    target_leads = models.ManyToManyField(Lead, blank=True, related_name="campaigns")
    sent_count = models.PositiveIntegerField(default=0)
    reply_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "outreach_campaigns"

    def __str__(self):
        return self.name


class OutreachLog(BaseModel):
    campaign = models.ForeignKey(OutreachCampaign, on_delete=models.CASCADE, related_name="logs")
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="outreach_logs")
    message_sent = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    replied = models.BooleanField(default=False)
    reply_text = models.TextField(blank=True)

    class Meta:
        db_table = "outreach_logs"
