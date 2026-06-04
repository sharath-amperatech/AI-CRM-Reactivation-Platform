from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.mixins import Base, OrgScopedMixin, TimestampMixin


class MessageStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SENT = "sent"
    FAILED = "failed"
    REJECTED = "rejected"


class Message(OrgScopedMixin, TimestampMixin, Base):
    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_lead_campaign", "lead_id", "campaign_id"),
        Index("ix_messages_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus, name="message_status", values_callable=lambda x: [e.value for e in x]),
        default=MessageStatus.DRAFT,
        nullable=False,
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    external_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # v2: prompt versioning + Langfuse observability
    prompt_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prompt_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    langfuse_trace_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reranker_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    meta: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    # Relationships
    lead: Mapped["Lead"] = relationship("Lead", back_populates="messages")  # noqa: F821
    campaign: Mapped["Campaign | None"] = relationship("Campaign", back_populates="messages")  # noqa: F821
    prompt_version: Mapped["PromptVersion | None"] = relationship("PromptVersion")  # noqa: F821
    approval: Mapped["Approval | None"] = relationship(  # noqa: F821
        "Approval", back_populates="message", uselist=False
    )
    replies: Mapped[list["Reply"]] = relationship(  # noqa: F821
        "Reply", back_populates="message", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Message lead={self.lead_id} status={self.status}>"
