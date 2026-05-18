"""
Follow-Up Agent — generates personalized follow-up messages.
"""
import logging
from .base_agent import BaseAgent
from .memory_service import MemoryService

logger = logging.getLogger("apps.ai_agents")


class FollowUpAgent(BaseAgent):
    agent_type = "followup"
    default_system_prompt = (
        "You are a follow-up specialist for {organization_name}. "
        "Write a warm, personalized follow-up message for {contact_name}. "
        "Reference previous conversation context. "
        "Keep it short (2-3 sentences). Don't be pushy."
    )

    def run(self, user_message: str = "") -> str:
        """Generate a follow-up message based on conversation history."""
        memory = MemoryService.get_or_create(self.lead)
        system_prompt = self.get_system_prompt()

        context_note = (
            f"Previous conversation summary: {memory.summary}\n"
            f"Lead interests: {', '.join(memory.extracted_interests) or 'unknown'}\n"
            f"Lead score: {self.lead.score}/100\n"
            f"Last status: {self.lead.status}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": context_note},
            {"role": "user", "content": "Generate a follow-up message for this lead."},
        ]

        response = self._call_llm(messages, temperature=0.8, max_tokens=300)
        logger.info("Follow-up generated for lead %s", self.lead.id)
        return response

    def generate_reminder(self, days_since_contact: int) -> str:
        """Generate a reminder message based on how long since last contact."""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {
                "role": "user",
                "content": (
                    f"It has been {days_since_contact} days since last contact with {self.lead.contact.full_name if self.lead.contact else 'this lead'}. "
                    f"Generate a re-engagement message. Lead interests: {self.lead.interests}."
                ),
            },
        ]
        return self._call_llm(messages, temperature=0.8, max_tokens=200)
