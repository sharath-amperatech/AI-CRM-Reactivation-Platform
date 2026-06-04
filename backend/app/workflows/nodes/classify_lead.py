from __future__ import annotations

import json

from pydantic import BaseModel, ValidationError, field_validator

from app.core.azure_openai import azure_client
from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.pii_scrubber import scrub_prompt
from app.observability import observe
from app.workflows.state import ReactivationState

logger = get_logger(__name__)

CLASSIFICATION_PROMPT = """You are an expert sales analyst. Classify this dormant lead based on CRM history.

Lead: {name} ({role}) at {company}
Deal Value: ${deal_value}
Inactive Days: {inactive_days}

Recent Activity History:
{activities}

Classify into one segment:
- pricing_objection: Lead cited budget/pricing concerns
- timing_issue: Lead asked to follow up later / budget cycle mismatch
- competitor_loss: Lead chose a competitor
- ghosted: Lead stopped responding without explanation
- no_decision_maker: Sales champion issue / champion left
- budget_constraints: Funding/budget constraints
- feature_gap: Product lacked a required feature
- unknown: Insufficient information

Respond with JSON:
{{"segment": "<segment>", "confidence": <0.0-1.0>, "reasoning": "<1-2 sentences>"}}"""


class ClassificationOutput(BaseModel):
    segment: str
    confidence: float
    reasoning: str

    @field_validator("segment")
    @classmethod
    def validate_segment(cls, v: str) -> str:
        valid = {
            "pricing_objection", "timing_issue", "competitor_loss", "ghosted",
            "no_decision_maker", "budget_constraints", "feature_gap", "unknown",
        }
        return v if v in valid else "unknown"

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


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


@observe(name="classify_lead")
async def classify_lead(state: ReactivationState) -> ReactivationState:
    if state.get("error"):
        return state

    lead = state.get("lead", {})
    context = state.get("crm_context_summary", "No context available.")
    activities_text = _format_activities(state.get("activities", []))
    settings = get_settings()

    prompt = CLASSIFICATION_PROMPT.format(
        name=lead.get("name", "Unknown"),
        role=lead.get("role", "Unknown"),
        company=lead.get("company", "Unknown"),
        deal_value=lead.get("deal_value", 0),
        inactive_days=lead.get("inactive_days", 0),
        activities=activities_text,
        context=context[:3000],
    )

    model = settings.AZURE_DEPLOYMENT_GPT41_MINI
    segment = "unknown"
    confidence = 0.5
    reasoning = ""

    @observe(name="classify_lead_llm", as_type="generation")
    async def _call_llm(prompt_text: str) -> tuple[str, float, str]:
        from langfuse import get_client  # type: ignore[import]
        resp = await azure_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt_text}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        get_client().update_current_generation(
            model=model,
            usage_details={
                "input": resp.usage.prompt_tokens,
                "output": resp.usage.completion_tokens,
                "total": resp.usage.total_tokens,
            },
            input=prompt_text,
            output=resp.choices[0].message.content,
        )
        parsed = ClassificationOutput.model_validate(json.loads(resp.choices[0].message.content))
        return parsed.segment, parsed.confidence, parsed.reasoning

    try:
        anon_prompt, _ = scrub_prompt(prompt, lead)
    except Exception as exc:
        logger.warning("classify_lead_pii_mask_failed", error=str(exc))
        anon_prompt = prompt

    try:
        segment, confidence, reasoning = await _call_llm(anon_prompt)
    except (ValidationError, json.JSONDecodeError) as exc:
        logger.warning("classify_lead_parse_error", error=str(exc))
        segment = lead.get("segment", "unknown")
        confidence = 0.5
        reasoning = f"Parse error — fallback to existing segment: {exc}"
    except Exception as exc:
        logger.warning("classify_lead_fallback", error=str(exc))
        segment = lead.get("segment", "unknown")
        confidence = 0.5
        reasoning = f"Classification unavailable: {exc}"

    logger.info(
        "workflow_classify_done",
        lead_id=state.get("lead_id"),
        segment=segment,
        confidence=confidence,
        model=model,
    )
    return {
        **state,
        "segment": segment,
        "confidence": confidence,
        "classification_reasoning": reasoning,
        "classification_model": model,
    }
