from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import Field

from app.models.campaign import CampaignStatus, MessageChannel
from app.schemas.common import APIModel


class CampaignCreate(APIModel):
    name: str
    description: str | None = None
    segment: str = "all"
    channel: MessageChannel = MessageChannel.EMAIL
    ab_test: bool = False
    config: dict = Field(default_factory=dict)


class CampaignUpdate(APIModel):
    name: str | None = None
    description: str | None = None
    segment: str | None = None
    channel: MessageChannel | None = None
    ab_test: bool | None = None
    config: dict | None = None


class CampaignRead(APIModel):
    id: uuid.UUID
    org_id: uuid.UUID
    name: str
    description: str | None
    status: CampaignStatus
    segment: str
    channel: MessageChannel
    ab_test: bool
    enrolled_leads: int
    open_rate: float
    reply_rate: float
    meetings_booked: int
    converted_leads: int
    revenue_recovered: float
    total_steps: int
    steps_completed: int
    started_at: datetime | None
    completed_at: datetime | None
    config: dict
    created_at: datetime
    updated_at: datetime


class EnrollmentLeadSummary(APIModel):
    id: uuid.UUID
    name: str
    company: str
    segment: str
    status: str


class CampaignEnrollmentRead(APIModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    enrolled_at: datetime
    status: str
    current_step: int
    lead: EnrollmentLeadSummary
