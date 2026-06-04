from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.logging import get_logger
from app.db.base import get_session_factory
from app.models.approval import Approval, ApprovalStatus
from app.models.lead import Lead, LeadSegment
from app.observability import observe
from app.workflows.state import ReactivationState

logger = get_logger(__name__)


@observe(name="human_approval")
async def human_approval(state: ReactivationState) -> ReactivationState:
    """Write Approval record to DB, then interrupt the graph to await human decision."""
    if state.get("error"):
        return state

    org_id = uuid.UUID(state["org_id"])
    lead_id = uuid.UUID(state["lead_id"])
    campaign_id = uuid.UUID(state["campaign_id"]) if state.get("campaign_id") else None
    message_id = uuid.UUID(state["message_id"])

    factory = get_session_factory()
    async with factory() as db:
        approval = Approval(
            org_id=org_id,
            message_id=message_id,
            lead_id=lead_id,
            campaign_id=campaign_id,
            status=ApprovalStatus.PENDING,
            confidence=state.get("confidence", 0.0),
            crm_context=state.get("crm_context_summary"),
            ai_reasoning=state.get("ai_reasoning"),
            retrieved_chunks=state.get("retrieved_chunks", []),
            trace_id=state.get("trace_id"),
        )
        db.add(approval)
        await db.commit()
        await db.refresh(approval)
        approval_id = str(approval.id)

        segment_value = state.get("segment", "unknown")
        lead_obj = await db.get(Lead, lead_id)
        if lead_obj:
            try:
                new_segment = LeadSegment(segment_value)
            except ValueError:
                new_segment = LeadSegment.UNKNOWN
            if lead_obj.segment != new_segment:
                lead_obj.segment = new_segment
                await db.commit()

    logger.info("workflow_approval_created", approval_id=approval_id, message_id=str(message_id))

    # Interrupt the graph — LangGraph will suspend here.
    # resume_workflow_after_approval Celery task resumes it.
    from langgraph.types import interrupt
    interrupt({"approval_id": approval_id, "reason": "human_review_required"})

    # Code below runs after resume
    return {**state, "approval_id": approval_id}
