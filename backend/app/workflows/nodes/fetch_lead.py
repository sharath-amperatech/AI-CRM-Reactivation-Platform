from __future__ import annotations

import uuid

from sqlalchemy import select

from app.core.logging import get_logger
from app.db.base import get_session_factory
from app.models.crm_activity import CRMActivity
from app.models.lead import Lead
from app.observability import observe
from app.workflows.state import ReactivationState

logger = get_logger(__name__)


@observe(name="fetch_lead")
async def fetch_lead(state: ReactivationState) -> ReactivationState:
    lead_id = uuid.UUID(state["lead_id"])
    org_id = uuid.UUID(state["org_id"])

    factory = get_session_factory()
    async with factory() as db:
        lead_result = await db.execute(
            select(Lead).where(Lead.id == lead_id, Lead.org_id == org_id, Lead.deleted_at.is_(None))
        )
        lead = lead_result.scalar_one_or_none()

        if lead is None:
            logger.error("workflow_lead_not_found", lead_id=str(lead_id))
            return {**state, "error": f"Lead {lead_id} not found"}

        activities_result = await db.execute(
            select(CRMActivity)
            .where(CRMActivity.lead_id == lead_id)
            .order_by(CRMActivity.occurred_at.desc())
            .limit(20)
        )
        activities = activities_result.scalars().all()

        lead_dict = {
            "id": str(lead.id),
            "name": lead.name,
            "company": lead.company,
            "email": lead.email,
            "role": lead.role,
            "segment": str(lead.segment),
            "status": str(lead.status),
            "confidence": lead.confidence,
            "deal_value": lead.deal_value,
            "inactive_days": lead.inactive_days,
        }

        activities_list = [
            {
                "id": str(a.id),
                "type": str(a.type),
                "occurred_at": str(a.occurred_at),
                "summary": a.summary,
                "content": a.content,
                "sentiment": str(a.sentiment) if a.sentiment else None,
            }
            for a in activities
        ]

    logger.info(
        "workflow_fetch_lead_done",
        lead_id=str(lead_id),
        activity_count=len(activities_list),
    )
    return {**state, "lead": lead_dict, "activities": activities_list, "error": None}
