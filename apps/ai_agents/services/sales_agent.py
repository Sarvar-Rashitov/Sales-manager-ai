"""
Sales Conversation Agent — persuasive replies, objection handling, recommendations.
"""
import logging
from .base_agent import BaseAgent
from .memory_service import MemoryService
from .sentiment_agent import SentimentAgent

logger = logging.getLogger("apps.ai_agents")


class SalesAgent(BaseAgent):
    agent_type = "sales"
    default_system_prompt = (
        "You are an expert AI sales representative for {organization_name}. "
        "Your goal is to guide {contact_name} toward a purchase decision. "
        "Handle objections professionally, highlight value, and suggest next steps. "
        "Lead status: {lead_status}. Budget: {budget}. "
        "Be persuasive but never pushy. Keep responses concise."
    )

    def run(self, user_message: str) -> str:
        MemoryService.add_user_message(self.lead, user_message)

        # Analyze sentiment in background
        sentiment_data = SentimentAgent(self.lead).analyze(user_message)
        MemoryService.update_extracted_data(
            self.lead,
            sentiment=sentiment_data.get("sentiment_score", 0),
            buying_intent=sentiment_data.get("buying_intent", 0),
        )

        # Check if RAG knowledge base has relevant info
        rag_context = self._get_rag_context(user_message)

        messages = self.build_messages(user_message)
        if rag_context:
            # Inject RAG context before the user message
            messages.insert(-1, {
                "role": "system",
                "content": f"Relevant product/company information:\n{rag_context}",
            })

        response = self._call_llm(messages, temperature=0.75)
        MemoryService.add_assistant_message(self.lead, response)

        # Summarize if conversation is getting long
        MemoryService.summarize_if_needed(self.lead)

        return response

    def _get_rag_context(self, query: str) -> str:
        """Try to retrieve relevant knowledge base context."""
        try:
            from apps.knowledge_base.services.rag_service import RAGService
            results = RAGService.search(
                organization=self.organization,
                query=query,
                top_k=3,
            )
            return "\n\n".join(results) if results else ""
        except Exception as e:
            logger.debug("RAG context unavailable: %s", e)
            return ""
