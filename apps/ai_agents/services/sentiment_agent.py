"""
Sentiment Analysis Agent — analyzes customer mood and buying intent.
"""
import json
import logging
from apps.crm.models import Lead
from apps.accounts.models import Organization
from .openai_client import chat_completion

logger = logging.getLogger("apps.ai_agents")


class SentimentAgent:
    agent_type = "sentiment"

    def __init__(self, lead: Lead):
        self.lead = lead
        self.organization = lead.organization

    def analyze(self, text: str) -> dict:
        """
        Returns dict with:
        - sentiment_score: float -1 (negative) to 1 (positive)
        - buying_intent: float 0 to 1
        - emotion: str (happy, frustrated, neutral, excited, etc.)
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "Analyze the sentiment and buying intent of this sales message. "
                    "Return JSON only with keys: "
                    "'sentiment_score' (float -1 to 1), "
                    "'buying_intent' (float 0 to 1), "
                    "'emotion' (string: happy/frustrated/neutral/excited/confused)."
                ),
            },
            {"role": "user", "content": text},
        ]

        result, _ = chat_completion(
            messages,
            temperature=0.1,
            max_tokens=150,
            agent_type=self.agent_type,
            organization_id=str(self.organization.id),
            lead_id=str(self.lead.id),
        )

        try:
            data = json.loads(result)
            return {
                "sentiment_score": float(data.get("sentiment_score", 0)),
                "buying_intent": float(data.get("buying_intent", 0)),
                "emotion": data.get("emotion", "neutral"),
            }
        except Exception:
            return {"sentiment_score": 0.0, "buying_intent": 0.0, "emotion": "neutral"}
