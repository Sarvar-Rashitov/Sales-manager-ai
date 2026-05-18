"""
Reception Agent — greets, detects language, classifies intent.
"""
import json
import logging
from .base_agent import BaseAgent
from .memory_service import MemoryService
from apps.crm.services.lead_service import LeadService

logger = logging.getLogger("apps.ai_agents")


class ReceptionAgent(BaseAgent):
    agent_type = "reception"
    default_system_prompt = (
        "You are a friendly AI receptionist for {organization_name}. "
        "Greet the customer warmly, detect their language, and understand their intent. "
        "Respond in the same language as the customer. "
        "Be concise and professional. Customer name: {contact_name}."
    )

    def run(self, user_message: str) -> str:
        # Detect language and intent first
        intent_data = self._classify_intent(user_message)
        language = intent_data.get("language", "en")
        intent = intent_data.get("intent", "general")

        # Update memory
        MemoryService.add_user_message(self.lead, user_message)
        self.memory.detected_language = language
        self.memory.save(update_fields=["detected_language", "updated_at"])

        # Generate greeting response
        messages = self.build_messages(user_message)
        response = self._call_llm(messages)

        MemoryService.add_assistant_message(self.lead, response)
        logger.info("Reception agent responded | lead=%s | intent=%s | lang=%s",
                    self.lead.id, intent, language)
        return response

    def _classify_intent(self, message: str) -> dict:
        """Quick classification call to understand what the user wants."""
        from .openai_client import chat_completion
        classify_messages = [
            {
                "role": "system",
                "content": (
                    "Classify this message. Return JSON only with keys: "
                    "'language' (ISO 639-1 code), "
                    "'intent' (one of: inquiry, complaint, purchase, support, other)."
                ),
            },
            {"role": "user", "content": message},
        ]
        result, _ = chat_completion(
            classify_messages,
            temperature=0.1,
            max_tokens=100,
            agent_type="reception_classifier",
            organization_id=str(self.organization.id),
        )
        try:
            return json.loads(result)
        except Exception:
            return {"language": "en", "intent": "other"}
