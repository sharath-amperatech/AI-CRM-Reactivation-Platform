from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.message import Message, MessageStatus

logger = get_logger(__name__)


class MessageService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_message(
        self,
        org_id: uuid.UUID,
        lead_id: uuid.UUID,
        campaign_id: uuid.UUID | None,
        channel: str,
        body: str,
        subject: str | None = None,
        status: MessageStatus = MessageStatus.DRAFT,
        metadata: dict | None = None,
    ) -> Message:
        message = Message(
            org_id=org_id,
            lead_id=lead_id,
            campaign_id=campaign_id,
            channel=channel,
            subject=subject,
            body=body,
            status=status,
            metadata=metadata or {},
        )
        self._db.add(message)
        await self._db.flush()
        logger.info("message_created", message_id=str(message.id), channel=channel)
        return message

    async def mark_sent(
        self, message_id: uuid.UUID, external_message_id: str | None = None
    ) -> Message:
        result = await self._db.execute(select(Message).where(Message.id == message_id))
        message = result.scalar_one()
        message.status = MessageStatus.SENT
        message.sent_at = datetime.now(timezone.utc)
        if external_message_id:
            message.external_message_id = external_message_id
        await self._db.flush()
        return message

    async def mark_failed(self, message_id: uuid.UUID, error: str) -> Message:
        result = await self._db.execute(select(Message).where(Message.id == message_id))
        message = result.scalar_one()
        message.status = MessageStatus.FAILED
        message.meta = {**message.meta, "send_error": error}
        await self._db.flush()
        return message
