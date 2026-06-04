from __future__ import annotations

import json
import uuid

from app.cache import SemanticCache
from app.core.azure_openai import azure_client
from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.base import get_session_factory
from app.models.message import MessageStatus
from app.observability import get_current_trace_id, observe
from app.prompt_registry import get_active_prompt
from app.services.embedding_service import EmbeddingService
from app.services.message_service import MessageService
from app.workflows.state import ReactivationState

logger = get_logger(__name__)

_cache = SemanticCache()


def _format_activities(activities: list) -> str:
    if not activities:
        return "No activity history available."
    lines = []
    for a in activities:
        occurred = a.get("occurred_at", "unknown date")
        atype = a.get("type", "")
        summary = a.get("summary", "")
        lines.append(f"- [{occurred}] {atype}: {summary}")
    return "\n".join(lines)


@observe(name="generate_message")
async def generate_message(state: ReactivationState) -> ReactivationState:
    if state.get("error"):
        return state

    lead = state.get("lead", {})
    settings = get_settings()
    trace_id = get_current_trace_id() or str(uuid.uuid4())
    org_id = uuid.UUID(state["org_id"])
    lead_id = uuid.UUID(state["lead_id"])
    campaign_id = uuid.UUID(state["campaign_id"]) if state.get("campaign_id") else None

    factory = get_session_factory()
    async with factory() as db:
        # ── 1. Load active prompt version ─────────────────────
        template_name = (
            f"sms_generation"
            if state.get("campaign_channel") == "sms"
            else "email_generation"
        )
        loaded_prompt = await get_active_prompt(db, org_id, template_name)

        # ── 2. Build the prompt text ───────────────────────────
        context = state.get("crm_context_summary", "")
        activities_text = _format_activities(state.get("activities", []))
        prompt_text = loaded_prompt.template.format(
            name=lead.get("name", ""),
            role=lead.get("role", ""),
            company=lead.get("company", ""),
            segment=state.get("segment", "unknown"),
            confidence=state.get("confidence", 0.5),
            deal_value=lead.get("deal_value", 0),
            inactive_days=lead.get("inactive_days", 0),
            activities=activities_text,
            context=context[:3000],
            reasoning=state.get("classification_reasoning", ""),
        )

        # ── 3. Semantic cache check ────────────────────────────
        embed_svc = EmbeddingService(db)
        cache_query = (
            f"{lead.get('name', '')} {lead.get('company', '')} "
            f"{state.get('segment', '')} {context[:200]}"
        )
        query_embedding = await embed_svc.embed_text(cache_query)
        cached_body = await _cache.get(query_embedding)

        subject: str
        body: str
        ai_reasoning: str

        if cached_body:
            logger.info("generate_message_cache_hit", lead_id=str(lead_id))
            # Cached responses are raw body strings; generate a minimal subject
            body = cached_body
            subject = f"Following up — {lead.get('company', '')}"
            ai_reasoning = "Response served from semantic cache."
        else:
            # ── 4. LLM call (azure_client + GPT-4.1-mini) ─────
            @observe(name="generate_message_llm", as_type="generation")
            async def _call_llm(prompt_text: str) -> tuple[str, str, str]:
                from langfuse import get_client  # type: ignore[import]
                resp = await azure_client.chat.completions.create(
                    model=settings.AZURE_DEPLOYMENT_GPT41_MINI,
                    messages=[{"role": "user", "content": prompt_text}],
                    response_format={"type": "json_object"},
                    temperature=0.7,
                )
                get_client().update_current_generation(
                    model=settings.AZURE_DEPLOYMENT_GPT41_MINI,
                    usage_details={
                        "input": resp.usage.prompt_tokens,
                        "output": resp.usage.completion_tokens,
                        "total": resp.usage.total_tokens,
                    },
                    input=prompt_text,
                    output=resp.choices[0].message.content,
                )
                parsed = json.loads(resp.choices[0].message.content)
                return (
                    parsed.get("subject", f"Following up — {lead.get('company', '')}"),
                    parsed.get("body", ""),
                    parsed.get("reasoning", ""),
                )

            try:
                subject, body, ai_reasoning = await _call_llm(prompt_text)
            except Exception as exc:
                logger.error("generate_message_failed", error=str(exc))
                return {**state, "error": f"Message generation failed: {exc}"}

            # Store in cache for future similar leads
            await _cache.set(query_embedding, body)

        # ── 5. Persist Message to DB with v2 fields ───────────
        reranker_scores = (state.get("retrieval_metadata") or {}).get("reranker_scores")
        msg_svc = MessageService(db)
        message = await msg_svc.create_message(
            org_id=org_id,
            lead_id=lead_id,
            campaign_id=campaign_id,
            channel=state.get("campaign_channel", "email"),
            subject=subject,
            body=body,
            status=MessageStatus.PENDING_APPROVAL,
            metadata={
                "trace_id": trace_id,
                "ai_reasoning": ai_reasoning,
                "prompt_version_id": str(loaded_prompt.version_id) if loaded_prompt.version_id else None,
                "prompt_from_db": loaded_prompt.from_db,
            },
        )

        # Patch v2 columns directly (prompt_version_id, langfuse_trace_id, reranker_scores)
        message.prompt_version_id = loaded_prompt.version_id
        message.langfuse_trace_id = trace_id
        if reranker_scores:
            message.reranker_scores = reranker_scores
        await db.commit()

    logger.info(
        "workflow_generate_done",
        message_id=str(message.id),
        trace_id=trace_id,
        prompt_from_db=loaded_prompt.from_db,
        cache_hit=cached_body is not None,
    )
    return {
        **state,
        "message_id": str(message.id),
        "subject": subject,
        "message_body": body,
        "final_message_body": body,
        "ai_reasoning": ai_reasoning,
        "trace_id": trace_id,
        "prompt_version_id": str(loaded_prompt.version_id) if loaded_prompt.version_id else None,
        "langfuse_trace_id": trace_id,
    }
