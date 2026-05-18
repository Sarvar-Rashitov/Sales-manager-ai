"""
Thin wrapper around the OpenAI client with logging and error handling.
"""
import time
import logging
from typing import Optional
from django.conf import settings

logger = logging.getLogger("apps.ai_agents")

try:
    from openai import OpenAI
    _client = OpenAI(api_key=settings.OPENAI_API_KEY)
except Exception:
    _client = None
    logger.warning("OpenAI client could not be initialized. Check OPENAI_API_KEY.")


def chat_completion(
    messages: list[dict],
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    organization_id=None,
    lead_id=None,
    agent_type: str = "unknown",
) -> tuple[str, dict]:
    """
    Call OpenAI chat completion.
    Returns (response_text, usage_dict).
    Logs the call to AILog automatically.
    """
    from apps.ai_agents.models import AILog

    if not _client:
        return "[AI unavailable - check OPENAI_API_KEY]", {}

    model = model or settings.OPENAI_MODEL
    start = time.time()
    error_msg = ""
    output = ""
    usage = {}

    try:
        response = _client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        output = response.choices[0].message.content or ""
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }
        success = True
    except Exception as e:
        error_msg = str(e)
        success = False
        logger.error("OpenAI error [%s]: %s", agent_type, e)

    latency = int((time.time() - start) * 1000)

    # Save audit log (best-effort)
    try:
        from apps.accounts.models import Organization
        org = Organization.objects.get(id=organization_id) if organization_id else None
        from apps.crm.models import Lead
        lead = Lead.objects.get(id=lead_id) if lead_id else None

        AILog.objects.create(
            organization=org,
            lead=lead,
            agent_type=agent_type,
            model=model,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            input_text=str(messages[-1].get("content", ""))[:2000],
            output_text=output[:2000],
            latency_ms=latency,
            success=success,
            error_message=error_msg,
        )
    except Exception as log_err:
        logger.warning("Could not save AILog: %s", log_err)

    return output, usage


def get_embedding(text: str) -> list[float]:
    """Get OpenAI embedding vector for a text string."""
    if not _client:
        return []
    try:
        response = _client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error("Embedding error: %s", e)
        return []
