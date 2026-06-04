from __future__ import annotations

from app.core.logging import get_logger
from app.observability import observe
from app.workflows.state import ReactivationState

logger = get_logger(__name__)


@observe(name="escalate")
async def escalate(state: ReactivationState) -> ReactivationState:
    lead_id = state.get("lead_id")
    reason = (
        state.get("send_error")
        or state.get("error")
        or (f"Reply intent: {state.get('reply_intent')}" if state.get("reply_intent") else "Manual review needed")
    )

    # Escalation actions:
    # 1. Notify assigned SDR via notification task
    # 2. Create internal task/ticket (future CRM write-back)
    # 3. Update lead status

    logger.info("workflow_escalated", lead_id=lead_id, reason=reason)

    try:
        from app.tasks.notification_tasks import send_escalation_notification
        send_escalation_notification.delay(
            lead_id=lead_id,
            reason=reason,
            trace_id=state.get("trace_id"),
        )
    except Exception as exc:
        logger.warning("escalation_notify_failed", error=str(exc))

    return {**state, "escalation_reason": reason}
