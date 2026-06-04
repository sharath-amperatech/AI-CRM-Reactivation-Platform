from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.mixins import Base, OrgScopedMixin, TimestampMixin


class CampaignEnrollment(OrgScopedMixin, TimestampMixin, Base):
    __tablename__ = "campaign_enrollments"
    __table_args__ = (
        UniqueConstraint("campaign_id", "lead_id", name="uq_campaign_enrollment"),
        Index("ix_enrollment_campaign", "campaign_id"),
        Index("ix_enrollment_lead", "lead_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default="enrolled", nullable=False
    )
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    workflow_thread_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    meta: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    # Relationships
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="enrollments")  # noqa: F821
    lead: Mapped["Lead"] = relationship("Lead", back_populates="enrollments")  # noqa: F821

    def __repr__(self) -> str:
        return f"<CampaignEnrollment campaign={self.campaign_id} lead={self.lead_id}>"
