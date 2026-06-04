"""Prompt registry — loads the active prompt version from DB for a given template name.

Usage:
    from app.prompt_registry import get_active_prompt

    loaded = await get_active_prompt(db, org_id, "email_generation")
    prompt_text = loaded.template.format(**vars)
    prompt_version_id = str(loaded.version_id)  # persist on Message

Falls back to hardcoded defaults if the DB has no active version, so the
system works out-of-the-box without seeding prompt_versions rows.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.prompt_version import PromptVersion

logger = get_logger(__name__)

# ── Hardcoded fallback templates (used when DB has no active version) ──────

_FALLBACK_TEMPLATES: dict[str, str] = {
    "email_generation": (
        "You are an expert sales copywriter specializing in reactivating dormant leads.\n\n"
        "Lead: {name} ({role}) at {company}\n"
        "Segment: {segment} | Confidence: {confidence:.0%}\n"
        "Deal Value: ${deal_value:,.0f} | Inactive: {inactive_days} days\n\n"
        "Recent Activity History:\n{activities}\n\n"
        "CRM Context (retrieved from history):\n{context}\n\n"
        "Classification Reasoning: {reasoning}\n\n"
        "Write a personalized reactivation email that:\n"
        "1. References specific details from their CRM history\n"
        "2. Addresses the likely objection/reason for inactivity\n"
        "3. Provides a clear value proposition\n"
        "4. Has a concrete call to action (meeting, demo, or call)\n"
        "5. Sounds human and consultative, NOT generic\n\n"
        'Respond with JSON:\n{{"subject": "<email subject>", "body": "<email body>", '
        '"reasoning": "<why this approach>"}}'
    ),
    "sms_generation": (
        "You are a sales rep sending a short SMS to a dormant lead.\n\n"
        "Lead: {name} at {company} | Segment: {segment}\n"
        "Recent Activity History: {activities}\n"
        "CRM Context: {context}\n\n"
        "Write a conversational SMS (under 160 characters) that reopens the conversation "
        "naturally. No marketing language.\n\n"
        'Respond with JSON:\n{{"body": "<sms body>", "reasoning": "<why this approach>"}}'
    ),
}


@dataclass
class LoadedPrompt:
    template: str
    version_id: uuid.UUID | None
    version_number: int | None
    from_db: bool


async def get_active_prompt(
    db: AsyncSession,
    org_id: uuid.UUID,
    template_name: str,
) -> LoadedPrompt:
    """Return the active prompt version for this org and template name.

    Falls back to the hardcoded default if no DB row is active.
    """
    try:
        result = await db.execute(
            select(PromptVersion).where(
                PromptVersion.org_id == org_id,
                PromptVersion.name == template_name,
                PromptVersion.is_active == True,  # noqa: E712
            )
        )
        version = result.scalar_one_or_none()
    except Exception as exc:
        logger.warning("prompt_registry_db_error", error=str(exc))
        version = None

    if version is not None:
        logger.info(
            "prompt_registry_loaded_from_db",
            template=template_name,
            version=version.version,
        )
        return LoadedPrompt(
            template=version.template,
            version_id=version.id,
            version_number=version.version,
            from_db=True,
        )

    # Fallback to hardcoded default
    fallback = _FALLBACK_TEMPLATES.get(template_name, _FALLBACK_TEMPLATES["email_generation"])
    logger.info("prompt_registry_using_fallback", template=template_name)
    return LoadedPrompt(
        template=fallback,
        version_id=None,
        version_number=None,
        from_db=False,
    )
