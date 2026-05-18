"""
Base agent class — all agents inherit from this.
"""
import logging
from abc import ABC, abstractmethod
from apps.crm.models import Lead
from apps.ai_agents.models import Prompt
from .openai_client import chat_completion
from .memory_service import MemoryService

logger = logging.getLogger("apps.ai_agents")


class BaseAgent(ABC):
    agent_type: str = "base"
    default_system_prompt: str = "You are a helpful AI sales assistant."

    def __init__(self, lead: Lead):
        self.lead = lead
        self.organization = lead.organization
        self.memory = MemoryService.get_or_create(lead)

    def get_system_prompt(self) -> str:
        """Load active prompt from DB, fall back to default."""
        prompt_obj = Prompt.objects.filter(
            organization=self.organization,
            agent_type=self.agent_type,
            is_active=True,
            is_default=True,
        ).first()
        if prompt_obj:
            return self._inject_lead_context(prompt_obj.system_prompt)
        return self._inject_lead_context(self.default_system_prompt)

    def _inject_lead_context(self, prompt: str) -> str:
        """Replace template variables in prompt with lead data."""
        contact = self.lead.contact
        return prompt.format(
            lead_title=self.lead.title,
            lead_status=self.lead.status,
            contact_name=contact.full_name if contact else "the customer",
            organization_name=self.organization.name,
            lead_score=self.lead.score,
            budget=self.lead.budget or "unknown",
        )

    def build_messages(self, user_message: str) -> list[dict]:
        system_prompt = self.get_system_prompt()
        messages = MemoryService.build_context(self.lead, system_prompt)
        messages.append({"role": "user", "content": user_message})
        return messages

    @abstractmethod
    def run(self, user_message: str) -> str:
        pass

    def _call_llm(self, messages: list[dict], temperature: float = 0.7,
                  max_tokens: int = 800) -> str:
        response, _ = chat_completion(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            organization_id=str(self.organization.id),
            lead_id=str(self.lead.id),
            agent_type=self.agent_type,
        )
        return response
