"""
Agent Router — decides which agent handles a given message.
"""
import logging
from apps.crm.models import Lead
from .reception_agent import ReceptionAgent
from .qualification_agent import QualificationAgent
from .sales_agent import SalesAgent
from .followup_agent import FollowUpAgent

logger = logging.getLogger("apps.ai_agents")


class AgentRouter:
    """
    Routes incoming messages to the appropriate agent based on lead status.

    Routing logic:
    - new → ReceptionAgent
    - contacted → QualificationAgent
    - qualified / demo / negotiation → SalesAgent
    - won / lost → SalesAgent (for re-engagement)
    """

    STATUS_AGENT_MAP = {
        Lead.Status.NEW: ReceptionAgent,
        Lead.Status.CONTACTED: QualificationAgent,
        Lead.Status.QUALIFIED: SalesAgent,
        Lead.Status.DEMO: SalesAgent,
        Lead.Status.NEGOTIATION: SalesAgent,
        Lead.Status.WON: SalesAgent,
        Lead.Status.LOST: FollowUpAgent,
    }

    @classmethod
    def route(cls, lead: Lead, message: str) -> str:
        """Process a message through the appropriate agent and return the response."""
        agent_class = cls.STATUS_AGENT_MAP.get(lead.status, SalesAgent)
        agent = agent_class(lead)

        logger.info(
            "Routing message | lead=%s | status=%s | agent=%s",
            lead.id, lead.status, agent_class.__name__,
        )

        response = agent.run(message)

        # Auto-advance status from new → contacted on first message
        if lead.status == Lead.Status.NEW:
            from apps.crm.services.lead_service import LeadService
            LeadService.update_status(lead, Lead.Status.CONTACTED)

        return response
