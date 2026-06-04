from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.logging import get_logger
from app.db.base import get_session_factory
from app.models.booking import Booking
from app.models.lead import Lead, LeadStatus
from app.observability import observe
from app.workflows.state import ReactivationState

logger = get_logger(__name__)


@observe(name="book_meeting")
async def book_meeting(state: ReactivationState) -> ReactivationState:
    if state.get("error"):
        return state

    lead_id = uuid.UUID(state["lead_id"])
    org_id = uuid.UUID(state["org_id"])

    # Calendly integration placeholder
    calendly_event_id = f"evt_{uuid.uuid4().hex[:12]}"
    booked_at = datetime.now(timezone.utc)

    factory = get_session_factory()
    async with factory() as db:
        booking = Booking(
            org_id=org_id,
            lead_id=lead_id,
            calendly_event_id=calendly_event_id,
            booked_at=booked_at,
            status="scheduled",
            metadata={"source": "reactivation_workflow", "trace_id": state.get("trace_id")},
        )
        db.add(booking)

        # Update lead status
        from sqlalchemy import select
        lead_result = await db.execute(select(Lead).where(Lead.id == lead_id))
        lead = lead_result.scalar_one_or_none()
        if lead:
            lead.status = LeadStatus.MEETING_BOOKED

        await db.commit()
        await db.refresh(booking)
        booking_id = str(booking.id)

    logger.info("workflow_meeting_booked", booking_id=booking_id, lead_id=str(lead_id))
    return {**state, "booking_id": booking_id}
