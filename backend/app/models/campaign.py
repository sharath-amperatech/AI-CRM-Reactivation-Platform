from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.mixins import Base, OrgScopedMixin, TimestampMixin


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class MessageChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class Campaign(OrgScopedMixin, TimestampMixin, Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus, name="campaign_status", values_callable=lambda x: [e.value for e in x]),
        default=CampaignStatus.DRAFT,
        nullable=False,
        index=True,
    )
    segment: Mapped[str] = mapped_column(String(50), default="all", nullable=False)
    channel: Mapped[MessageChannel] = mapped_column(
        Enum(MessageChannel, name="message_channel", values_callable=lambda x: [e.value for e in x]),
        default=MessageChannel.EMAIL,
        nullable=False,
    )
    ab_test: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Performance metrics (denormalized for fast reads)
    enrolled_leads: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    open_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reply_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    meetings_booked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    converted_leads: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    revenue_recovered: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Workflow progress
    total_steps: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    steps_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship(  # noqa: F821
        "Organization", back_populates="campaigns"
    )
    enrollments: Mapped[list["CampaignEnrollment"]] = relationship(  # noqa: F821
        "CampaignEnrollment", back_populates="campaign", cascade="all, delete-orphan"
    )
    messages: Mapped[list["Message"]] = relationship(  # noqa: F821
        "Message", back_populates="campaign"
    )

    def __repr__(self) -> str:
        return f"<Campaign {self.name} status={self.status}>"
