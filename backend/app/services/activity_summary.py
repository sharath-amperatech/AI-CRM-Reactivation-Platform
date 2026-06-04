from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.azure_openai import azure_client
from app.core.config import get_settings
from app.core.logging import get_logger

if TYPE_CHECKING:
    from app.models.crm_activity import CRMActivity

logger = get_logger(__name__)

_SUMMARY_PROMPT = (
    "You are a CRM assistant. Summarize the following CRM activity in ONE concise sentence "
    "(max 20 words). Start your response with an action verb such as 'Sent', 'Followed up', "
    "'Proposed', 'Called', or 'Met'. Do NOT reproduce the email greeting or the sender's name.\n\n"
    "Activity type: {activity_type}\n"
    "Content:\n{content}"
)

_LEAD_SUMMARY_PROMPT = (
    "Write a 2-3 sentence CRM summary for this sales lead based on their activity history. "
    "Focus on: what stage the deal reached, key objections or blockers, and current status.\n\n"
    "Activities:\n{activities}"
)


async def generate_activity_summary(activity_type: str, content: str) -> str:
    """Generate a one-sentence summary via Azure OpenAI; fallback to truncation."""
    if not content.strip():
        return ""
    settings = get_settings()
    try:
        response = await azure_client.chat.completions.create(
            model=settings.AZURE_DEPLOYMENT_GPT41_MINI,
            messages=[
                {
                    "role": "user",
                    "content": _SUMMARY_PROMPT.format(
                        activity_type=activity_type,
                        content=content[:500],
                    ),
                }
            ],
        )
        result = response.choices[0].message.content.strip()
        logger.info("activity_summary_generated", type=activity_type, result=result)
        return result
    except Exception as exc:
        logger.warning("summary_generation_failed", type=activity_type, error=str(exc))
        return content[:100]


async def generate_lead_crm_summary(activities: list["CRMActivity"]) -> str:
    """Generate a 2-3 sentence CRM summary for a lead from their activity history."""
    if not activities:
        return ""
    settings = get_settings()
    recent = activities[-8:]
    activity_lines = "\n".join(
        f"- [{a.type.value.upper()}] {a.summary or (a.content[:80] if a.content else '(no content)')}"
        for a in recent
    )
    try:
        response = await azure_client.chat.completions.create(
            model=settings.AZURE_DEPLOYMENT_GPT41_MINI,
            messages=[
                {
                    "role": "user",
                    "content": _LEAD_SUMMARY_PROMPT.format(activities=activity_lines),
                }
            ],
        )
        result = response.choices[0].message.content.strip()
        logger.info("lead_crm_summary_generated", activity_count=len(recent), result=result)
        return result
    except Exception as exc:
        logger.warning("lead_summary_generation_failed", error=str(exc))
        return ""
