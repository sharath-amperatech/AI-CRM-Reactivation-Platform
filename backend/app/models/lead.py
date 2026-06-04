from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.mixins import Base, OrgScopedMixin, SoftDeleteMixin, TimestampMixin


class LeadSegment(str, enum.Enum):
    PRICING_OBJECTION = "pricing_objection"
    TIMING_ISSUE = "timing_issue"
    COMPETITOR_LOSS = "competitor_loss"
    GHOSTED = "ghosted"
    NO_DECISION_MAKER = "no_decision_maker"
    BUDGET_CONSTRAINTS = "budget_constraints"
    FEATURE_GAP = "feature_gap"
    UNKNOWN = "unknown"


class LeadStatus(str, enum.Enum):
    DORMANT = "dormant"
    ACTIVE = "active"
    REACTIVATED = "reactivated"
    LOST = "lost"
    MEETING_BOOKED = "meeting_booked"


class Lead(OrgScopedMixin, SoftDeleteMixin, TimestampMixin, Base):
    __tablename__ = "leads"
    __table_args__ = (
        Index("ix_leads_org_status_segment", "org_id", "status", "segment"),
        Index("ix_leads_org_inactive_days", "org_id", "inactive_days"),
        Index("ix_leads_assigned", "assigned_to_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    hubspot_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    segment: Mapped[LeadSegment] = mapped_column(
        Enum(LeadSegment, name="lead_segment", values_callable=lambda x: [e.value for e in x]),
        default=LeadSegment.UNKNOWN,
        nullable=False,
    )
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, name="lead_status", values_callable=lambda x: [e.value for e in x]),
        default=LeadStatus.DORMANT,
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    deal_value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    inactive_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_activity_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    assigned_to_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    company_size: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    meta: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)
    crm_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(  # noqa: F821
        "Organization", back_populates="leads"
    )
    assigned_to: Mapped["User | None"] = relationship(  # noqa: F821
        "User", foreign_keys=[assigned_to_id]
    )
    activities: Mapped[list["CRMActivity"]] = relationship(  # noqa: F821
        "CRMActivity", back_populates="lead", cascade="all, delete-orphan"
    )
    enrollments: Mapped[list["CampaignEnrollment"]] = relationship(  # noqa: F821
        "CampaignEnrollment", back_populates="lead"
    )
    messages: Mapped[list["Message"]] = relationship(  # noqa: F821
        "Message", back_populates="lead"
    )
    bookings: Mapped[list["Booking"]] = relationship(  # noqa: F821
        "Booking", back_populates="lead"
    )

    def __repr__(self) -> str:
        return f"<Lead {self.name} ({self.company}) status={self.status}>"
