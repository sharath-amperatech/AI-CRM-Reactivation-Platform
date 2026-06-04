from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.logging import get_logger
from app.db.base import get_session_factory
from app.models.approval import Approval
from app.observability import observe
from app.services.message_service import MessageService
from app.services.resend_service import ResendService
from app.services.twilio_service import TwilioService
from app.workflows.state import ReactivationState

logger = get_logger(__name__)


@observe(name="send_message")
async def send_message(state: ReactivationState) -> ReactivationState:
    if state.get("error"):
        return state
    if state.get("approval_status") == "rejected":
        logger.info("workflow_send_skipped_rejected", lead_id=state.get("lead_id"))
        return state

    lead = state.get("lead", {})
    message_body = state.get("final_message_body") or state.get("message_body", "")
    subject = state.get("subject", "")
    message_id = uuid.UUID(state["message_id"])

    channel = "email"

    factory = get_session_factory()
    async with factory() as db:
        msg_svc = MessageService(db)
        try:
            if channel == "email":
                svc = ResendService()
                external_id = await svc.send_email(
                    to=lead["email"],
                    subject=subject,
                    html=ResendService().text_to_html(message_body),
                    metadata={"lead_id": state["lead_id"], "trace_id": state.get("trace_id")},
                )
            else:
                svc = TwilioService()
                external_id = await svc.send_sms(to=lead.get("phone", ""), body=message_body)

            await msg_svc.mark_sent(message_id=message_id, external_message_id=external_id)
            await db.commit()

            sent_at = datetime.now(timezone.utc).isoformat()
            logger.info("workflow_message_sent", lead_id=state["lead_id"], external_id=external_id)
            return {
                **state,
                "sent_at": sent_at,
                "send_error": None,
                "external_message_id": external_id,
            }

        except Exception as exc:
            await msg_svc.mark_failed(message_id=message_id, error=str(exc))
            await db.commit()
            logger.error("workflow_send_failed", error=str(exc))
            return {**state, "send_error": str(exc), "sent_at": None}
