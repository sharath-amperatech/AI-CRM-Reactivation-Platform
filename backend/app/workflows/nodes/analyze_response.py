from __future__ import annotations

import json

from app.core.azure_openai import azure_client
from app.core.config import get_settings
from app.core.logging import get_logger
from app.observability import observe
from app.workflows.state import ReactivationState

logger = get_logger(__name__)

ANALYSIS_PROMPT = """Analyze this reply to a sales reactivation email.

Original outreach context:
Lead: {lead_name} at {company}
Segment: {segment}

Reply received:
{reply_body}

Classify the reply:
- sentiment: positive | neutral | negative
- intent: interested | not_interested | booked | needs_info | unsubscribe

Respond with JSON: {{"sentiment": "...", "intent": "...", "summary": "..."}}"""


@observe(name="analyze_response")
async def analyze_response(state: ReactivationState) -> ReactivationState:
    if state.get("error"):
        return state

    reply_body = state.get("reply_body")
    if not reply_body:
        return {**state, "reply_sentiment": None, "reply_intent": None}

    lead = state.get("lead", {})
    settings = get_settings()

    prompt = ANALYSIS_PROMPT.format(
        lead_name=lead.get("name", ""),
        company=lead.get("company", ""),
        segment=state.get("segment", "unknown"),
        reply_body=reply_body[:2000],
    )

    @observe(name="analyze_response_llm", as_type="generation")
    async def _call_llm(prompt_text: str) -> tuple[str, str]:
        from langfuse import get_client  # type: ignore[import]
        resp = await azure_client.chat.completions.create(
            model=settings.AZURE_DEPLOYMENT_GPT5_NANO,
            messages=[{"role": "user", "content": prompt_text}],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        get_client().update_current_generation(
            model=settings.AZURE_DEPLOYMENT_GPT5_NANO,
            usage_details={
                "input": resp.usage.prompt_tokens,
                "output": resp.usage.completion_tokens,
                "total": resp.usage.total_tokens,
            },
            input=prompt_text,
            output=resp.choices[0].message.content,
        )
        parsed = json.loads(resp.choices[0].message.content)
        return parsed.get("sentiment", "neutral"), parsed.get("intent", "needs_info")

    try:
        sentiment, intent = await _call_llm(prompt)
    except Exception as exc:
        logger.warning("analyze_response_failed", error=str(exc))
        sentiment = "neutral"
        intent = "needs_info"

    logger.info("workflow_analyze_done", sentiment=sentiment, intent=intent)
    return {**state, "reply_sentiment": sentiment, "reply_intent": intent}
