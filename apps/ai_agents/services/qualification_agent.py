"""
Qualification Agent — asks qualifying questions, scores the lead.
"""
import json
import logging
from .base_agent import BaseAgent
from .memory_service import MemoryService
from apps.crm.services.lead_service import LeadService

logger = logging.getLogger("apps.ai_agents")

QUALIFICATION_QUESTIONS = [
    "What specific problem are you trying to solve?",
    "What is your approximate budget for this solution?",
    "What is your timeline for implementation?",
    "Who else is involved in the decision-making process?",
    "Have you tried other solutions before?",
]


class QualificationAgent(BaseAgent):
    agent_type = "qualification"
    default_system_prompt = (
        "You are an expert sales qualification specialist for {organization_name}. "
        "Your goal is to qualify leads by asking smart, conversational questions. "
        "Ask one question at a time. Be friendly and natural. "
        "Customer: {contact_name}. Current lead score: {lead_score}/100."
    )

    def run(self, user_message: str) -> str:
        MemoryService.add_user_message(self.lead, user_message)

        # Score the lead based on conversation
        score_data = self._score_lead()
        new_score = score_data.get("score", self.lead.score)
        budget = score_data.get("budget")
        interests = score_data.get("interests", [])

        # Update lead and memory
        LeadService.update_score(self.lead, new_score)
        MemoryService.update_extracted_data(
            self.lead,
            budget=budget,
            interests=interests,
        )

        # Generate next qualifying question or move forward
        messages = self.build_messages(user_message)
        response = self._call_llm(messages)

        MemoryService.add_assistant_message(self.lead, response)

        # Auto-qualify if score is high enough
        if new_score >= 60 and self.lead.status == "new":
            LeadService.update_status(self.lead, "qualified")
            logger.info("Lead auto-qualified: %s (score=%s)", self.lead.id, new_score)

        return response

    def _score_lead(self) -> dict:
        """Use AI to extract score, budget, interests from conversation."""
        from .openai_client import chat_completion
        messages = [
            {
                "role": "system",
                "content": (
                    "Analyze this sales conversation and return JSON with: "
                    "'score' (0-100 lead quality), "
                    "'budget' (number or null), "
                    "'interests' (list of strings). "
                    "Return only valid JSON."
                ),
            },
            *self.memory.get_recent_messages(15),
        ]
        result, _ = chat_completion(
            messages,
            temperature=0.1,
            max_tokens=200,
            agent_type="qualification_scorer",
            organization_id=str(self.organization.id),
            lead_id=str(self.lead.id),
        )
        try:
            return json.loads(result)
        except Exception:
            return {"score": self.lead.score, "budget": None, "interests": []}
