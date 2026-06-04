from __future__ import annotations

import enum
import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.mixins import Base, OrgScopedMixin, TimestampMixin


class ActivityType(str, enum.Enum):
    EMAIL = "email"
    CALL = "call"
    MEETING = "meeting"
    NOTE = "note"
    DEAL_UPDATE = "deal_update"


class SentimentType(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class CRMActivity(OrgScopedMixin, TimestampMixin, Base):
    __tablename__ = "crm_activities"
    __table_args__ = (
        Index("ix_crm_activity_lead_occurred", "lead_id", "occurred_at"),
        # IVFFlat index on embedding is created via raw DDL in the migration
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[ActivityType] = mapped_column(
        Enum(ActivityType, name="activity_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    sentiment: Mapped[SentimentType | None] = mapped_column(
        Enum(SentimentType, name="sentiment_type", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hubspot_engagement_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )

    # PGVector embedding column (1536 dims for text-embedding-3-small)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    embedding_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("embedding_versions.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Parent-child chunking: child chunks point to their parent
    parent_chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_activities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    chunk_index: Mapped[int | None] = mapped_column(nullable=True)

    meta: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    # Relationships
    lead: Mapped["Lead"] = relationship("Lead", back_populates="activities")  # noqa: F821
    embedding_version: Mapped["EmbeddingVersion | None"] = relationship(  # noqa: F821
        "EmbeddingVersion"
    )
    parent_chunk: Mapped["CRMActivity | None"] = relationship(
        "CRMActivity", remote_side="CRMActivity.id", foreign_keys=[parent_chunk_id]
    )
    child_chunks: Mapped[list["CRMActivity"]] = relationship(
        "CRMActivity", foreign_keys=[parent_chunk_id], back_populates="parent_chunk"
    )

    def __repr__(self) -> str:
        return f"<CRMActivity {self.type} lead={self.lead_id} at={self.occurred_at}>"
