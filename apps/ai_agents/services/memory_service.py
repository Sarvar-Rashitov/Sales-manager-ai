"""
AI Memory Service — manages conversation context per lead.
"""
import logging
from apps.crm.models import Lead
from apps.ai_agents.models import ConversationMemory
from .openai_client import chat_completion

logger = logging.getLogger("apps.ai_agents")


class MemoryService:

    @staticmethod
    def get_or_create(lead: Lead) -> ConversationMemory:
        memory, _ = ConversationMemory.objects.get_or_create(lead=lead)
        return memory

    @staticmethod
    def add_user_message(lead: Lead, content: str) -> ConversationMemory:
        memory = MemoryService.get_or_create(lead)
        memory.add_message("user", content)
        return memory

    @staticmethod
    def add_assistant_message(lead: Lead, content: str) -> ConversationMemory:
        memory = MemoryService.get_or_create(lead)
        memory.add_message("assistant", content)
        return memory

    @staticmethod
    def build_context(lead: Lead, system_prompt: str, n_recent: int = 10) -> list[dict]:
        """Build the messages list to send to OpenAI, including memory."""
        memory = MemoryService.get_or_create(lead)
        messages = [{"role": "system", "content": system_prompt}]

        # Inject summary if available
        if memory.summary:
            messages.append({
                "role": "system",
                "content": f"Conversation summary so far: {memory.summary}",
            })

        # Inject recent messages
        messages.extend(memory.get_recent_messages(n_recent))
        return messages

    @staticmethod
    def summarize_if_needed(lead: Lead, threshold: int = 20) -> None:
        """Summarize conversation when it gets long to save tokens."""
        memory = MemoryService.get_or_create(lead)
        if len(memory.messages) < threshold:
            return

        summary_prompt = [
            {"role": "system", "content": "Summarize this sales conversation in 3-5 sentences. Focus on: customer needs, budget, objections, and next steps."},
            *memory.messages,
        ]
        summary, _ = chat_completion(
            summary_prompt,
            agent_type="memory_summarizer",
            organization_id=str(lead.organization_id),
            lead_id=str(lead.id),
        )
        memory.summary = summary
        memory.messages = memory.messages[-10:]  # keep only last 10 after summarizing
        memory.save(update_fields=["summary", "messages", "updated_at"])
        logger.info("Summarized memory for lead %s", lead.id)

    @staticmethod
    def update_extracted_data(lead: Lead, budget=None, interests: list = None,
                               sentiment: float = None, buying_intent: float = None) -> None:
        memory = MemoryService.get_or_create(lead)
        update_fields = ["updated_at"]

        if budget is not None:
            memory.extracted_budget = budget
            update_fields.append("extracted_budget")
        if interests is not None:
            memory.extracted_interests = interests
            update_fields.append("extracted_interests")
        if sentiment is not None:
            memory.sentiment_score = sentiment
            update_fields.append("sentiment_score")
        if buying_intent is not None:
            memory.buying_intent_score = buying_intent
            update_fields.append("buying_intent_score")

        memory.save(update_fields=update_fields)
