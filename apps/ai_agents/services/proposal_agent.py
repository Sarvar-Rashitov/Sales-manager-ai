"""
Proposal Generator Agent — creates sales proposals and quotations.
"""
import logging
from .base_agent import BaseAgent
from .memory_service import MemoryService

logger = logging.getLogger("apps.ai_agents")


class ProposalAgent(BaseAgent):
    agent_type = "proposal"
    default_system_prompt = (
        "You are a professional proposal writer for {organization_name}. "
        "Create a compelling, personalized sales proposal for {contact_name}. "
        "Budget: {budget}. Include: executive summary, solution overview, pricing, next steps."
    )

    def run(self, user_message: str = "") -> str:
        return self.generate_proposal()

    def generate_proposal(self) -> str:
        memory = MemoryService.get_or_create(self.lead)
        contact = self.lead.contact

        context = (
            f"Customer: {contact.full_name if contact else 'Valued Customer'}\n"
            f"Company: {contact.company.name if contact and contact.company else 'N/A'}\n"
            f"Budget: {memory.extracted_budget or self.lead.budget or 'To be discussed'}\n"
            f"Interests: {', '.join(memory.extracted_interests) or 'General inquiry'}\n"
            f"Conversation summary: {memory.summary or 'Initial contact'}"
        )

        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "system", "content": f"Customer context:\n{context}"},
            {"role": "user", "content": "Generate a professional sales proposal."},
        ]

        proposal = self._call_llm(messages, temperature=0.6, max_tokens=1500)
        logger.info("Proposal generated for lead %s", self.lead.id)
        return proposal

    def generate_quotation(self, items: list[dict]) -> str:
        """Generate a price quotation from a list of items."""
        items_text = "\n".join(
            f"- {item['name']}: ${item['price']} x {item.get('qty', 1)}"
            for item in items
        )
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {
                "role": "user",
                "content": f"Create a formal quotation for:\n{items_text}\nCustomer: {self.lead.contact.full_name if self.lead.contact else 'Customer'}",
            },
        ]
        return self._call_llm(messages, temperature=0.4, max_tokens=800)
