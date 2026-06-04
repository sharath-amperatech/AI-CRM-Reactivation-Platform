from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.pii_scrubber import scrub_metadata
from app.integrations.hubspot.client import HubSpotClient
from app.models.crm_activity import ActivityType, CRMActivity
from app.models.lead import Lead
from app.services.activity_summary import generate_activity_summary

logger = get_logger(__name__)

_HUBSPOT_TYPE_MAP: dict[str, ActivityType] = {
    "EMAIL": ActivityType.EMAIL,
    "CALL": ActivityType.CALL,
    "MEETING": ActivityType.MEETING,
    "NOTE": ActivityType.NOTE,
    "TASK": ActivityType.NOTE,
}


class HubSpotSyncService:
    """Transforms HubSpot contacts + engagements into Lead + CRMActivity records."""

    def __init__(self, client: HubSpotClient, db: AsyncSession) -> None:
        self._client = client
        self._db = db

    async def sync_contacts(self, org_id: str, incremental: bool = True) -> dict[str, int]:
        """Sync HubSpot contacts to leads table. Returns counts."""
        created = updated = skipped = 0
        after = None

        while True:
            page = await self._client.get_contacts(limit=100, after=after)
            contacts = page.get("results", [])

            for contact in contacts:
                result = await self._upsert_contact(org_id, contact)
                if result == "created":
                    created += 1
                elif result == "updated":
                    updated += 1
                else:
                    skipped += 1

            paging = page.get("paging", {})
            after = paging.get("next", {}).get("after")
            if not after:
                break

        logger.info(
            "hubspot_sync_complete",
            org_id=org_id,
            created=created,
            updated=updated,
            skipped=skipped,
        )
        return {"created": created, "updated": updated, "skipped": skipped}

    async def _upsert_contact(self, org_id: str, contact: dict[str, Any]) -> str:
        """Upsert a single HubSpot contact as a Lead record. Placeholder — implement."""
        # TODO: Implement full upsert logic using LeadRepository
        return "skipped"

    async def sync_engagements(self, org_id: str, hubspot_contact_id: str) -> int:
        """Sync engagements for a contact as CRMActivity records. Returns count created."""
        engagements_data = await self._client.get_engagements(hubspot_contact_id)
        engagements = engagements_data.get("results", [])
        created = 0

        for engagement_ref in engagements:
            try:
                detail = await self._client.get_engagement_detail(
                    engagement_ref["id"]
                )
                await self._upsert_engagement(org_id, hubspot_contact_id, detail)
                created += 1
            except Exception as exc:
                logger.warning(
                    "engagement_sync_failed",
                    engagement_id=engagement_ref.get("id"),
                    error=str(exc),
                )

        return created

    async def _upsert_engagement(
        self, org_id: str, hubspot_contact_id: str, detail: dict[str, Any]
    ) -> None:
        """Upsert a HubSpot engagement as a CRMActivity with AI-generated summary."""
        engagement = detail.get("engagement", {})
        metadata = detail.get("metadata", {})

        hubspot_engagement_id = str(engagement.get("id", ""))
        if not hubspot_engagement_id:
            return

        # Find the local lead via hubspot_id
        result = await self._db.execute(
            select(Lead).where(Lead.hubspot_id == hubspot_contact_id)
        )
        lead = result.scalar_one_or_none()
        if not lead:
            logger.warning("engagement_lead_not_found", hubspot_contact_id=hubspot_contact_id)
            return

        # Map engagement type
        hs_type = engagement.get("type", "NOTE").upper()
        activity_type = _HUBSPOT_TYPE_MAP.get(hs_type, ActivityType.NOTE)

        # Extract content and author from metadata
        content: str = metadata.get("body") or metadata.get("text") or ""
        from_info = metadata.get("from", {}) or {}
        first = from_info.get("firstName", "")
        last = from_info.get("lastName", "")
        email = from_info.get("email", "")
        author = f"{first} {last}".strip() or email or None

        # Convert HubSpot ms timestamp to UTC datetime
        ts_ms = engagement.get("timestamp")
        occurred_at = (
            datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            if ts_ms
            else datetime.now(tz=timezone.utc)
        )

        # Generate summary via Azure OpenAI; fall back to truncated content on failure
        summary = await self._generate_summary(activity_type.value, content)

        # Check for existing activity to decide insert vs update
        existing_result = await self._db.execute(
            select(CRMActivity).where(
                CRMActivity.hubspot_engagement_id == hubspot_engagement_id
            )
        )
        activity = existing_result.scalar_one_or_none()

        if activity:
            activity.summary = summary
            activity.content = content
            activity.author = author
            activity.occurred_at = occurred_at
            activity.type = activity_type
        else:
            activity = CRMActivity(
                id=uuid.uuid4(),
                org_id=lead.org_id,
                lead_id=lead.id,
                type=activity_type,
                occurred_at=occurred_at,
                summary=summary,
                content=content,
                author=author,
                hubspot_engagement_id=hubspot_engagement_id,
                meta=scrub_metadata(metadata),
            )
            self._db.add(activity)

        await self._db.flush()

        # Dispatch embedding generation asynchronously
        from app.tasks.embedding_tasks import embed_activities_batch
        embed_activities_batch.delay([str(activity.id)], str(lead.org_id))

        logger.info(
            "engagement_upserted",
            hubspot_engagement_id=hubspot_engagement_id,
            activity_id=str(activity.id),
            type=activity_type.value,
        )

    async def _generate_summary(self, activity_type: str, content: str) -> str:
        return await generate_activity_summary(activity_type, content)
