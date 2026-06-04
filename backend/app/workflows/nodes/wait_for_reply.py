from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select

from app.core.logging import get_logger
from app.db.base import get_session_factory
from app.models.reply import Reply
from app.observability import observe
from app.workflows.state import ReactivationState

logger = get_logger(__name__)

MAX_WAIT_SECONDS = 60 * 60 * 24 * 7  # 7 days (in practice, Celery schedules the check)
POLL_INTERVAL = 30


@observe(name="wait_for_reply")
async def wait_for_reply(state: ReactivationState) -> ReactivationState:
    """Poll for an inbound Reply record linked to this message."""
    if state.get("error") or state.get("send_error"):
        return state

    message_id_str = state.get("message_id")
    if not message_id_str:
        return state

    message_id = uuid.UUID(message_id_str)
    factory = get_session_factory()

    # Check once — in production this node is re-invoked by a scheduled task
    async with factory() as db:
        result = await db.execute(
            select(Reply)
            .where(Reply.message_id == message_id)
            .order_by(Reply.received_at.asc())
            .limit(1)
        )
        reply = result.scalar_one_or_none()

    if reply is None:
        logger.info("workflow_no_reply_yet", message_id=message_id_str)
        # In a durable execution setup, interrupt here and reschedule
        return {**state, "reply_id": None, "reply_body": None, "reply_received_at": None}

    logger.info("workflow_reply_received", reply_id=str(reply.id))
    return {
        **state,
        "reply_id": str(reply.id),
        "reply_body": reply.body,
        "reply_received_at": str(reply.received_at),
    }
