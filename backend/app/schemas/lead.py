from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import Field, field_validator

from app.models.lead import LeadSegment, LeadStatus
from app.schemas.common import APIModel


class LeadEnrollmentSummary(APIModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    campaign_name: str
    status: str
    enrolled_at: datetime


class _LeadBase(APIModel):
    id: uuid.UUID
    org_id: uuid.UUID
    hubspot_id: str | None
    name: str
    company: str
    email: str
    phone: str | None
    role: str | None
    segment: LeadSegment
    status: LeadStatus
    confidence: float
    deal_value: float
    inactive_days: int
    last_activity_at: datetime | None
    assigned_to_id: uuid.UUID | None
    industry: str | None
    company_size: str | None
    location: str | None
    source: str | None
    tags: list
    meta: dict = Field(serialization_alias="metadata")
    crm_summary: str | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("segment", mode="before")
    @classmethod
    def coerce_segment(cls, v):
        if isinstance(v, str):
            return LeadSegment(v)
        return v

    @field_validator("status", mode="before")
    @classmethod
    def coerce_status(cls, v):
        if isinstance(v, str):
            return LeadStatus(v)
        return v


class LeadListRead(_LeadBase):
    """Used by the paginated list endpoint — no enrollment data to avoid lazy-load errors."""
    pass


class LeadRead(_LeadBase):
    """Used by the single-lead detail endpoint — includes eagerly-loaded enrollment data."""
    enrollments: list[LeadEnrollmentSummary] = []

    @field_validator("enrollments", mode="before")
    @classmethod
    def build_enrollments(cls, v):
        if not v:
            return []
        result = []
        for e in v:
            try:
                result.append({
                    "id": e.id,
                    "campaign_id": e.campaign_id,
                    "campaign_name": e.campaign.name,
                    "status": e.status,
                    "enrolled_at": e.enrolled_at,
                })
            except Exception:
                pass
        return result


class LeadUpdate(APIModel):
    name: str | None = None
    company: str | None = None
    email: str | None = None
    phone: str | None = None
    role: str | None = None
    segment: LeadSegment | None = None
    status: LeadStatus | None = None
    assigned_to_id: uuid.UUID | None = None
    industry: str | None = None
    company_size: str | None = None
    location: str | None = None
    tags: list | None = None
    meta: dict | None = Field(None, alias="metadata")


class LeadFilter(APIModel):
    segment: LeadSegment | None = None
    status: LeadStatus | None = None
    assigned_to_id: uuid.UUID | None = None
    search: str | None = None
    min_deal_value: float | None = None
    min_inactive_days: int | None = None


class CRMActivityRead(APIModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    type: str
    occurred_at: datetime
    summary: str | None
    content: str | None
    sentiment: str | None
    author: str | None
    meta: dict = Field(serialization_alias="metadata")
    created_at: datetime


class LeadMessageRead(APIModel):
    id: uuid.UUID
    channel: str
    subject: str | None
    body: str
    status: str
    sent_at: datetime | None
    created_at: datetime
    approval_id: uuid.UUID | None = None
    confidence: float = 0.0
    ai_reasoning: str | None = None
    retrieved_chunks: list = []
    trace_id: str | None = None
    approval_status: str | None = None


class AuditLogRead(APIModel):
    id: uuid.UUID
    action: str
    resource_type: str
    resource_id: str | None
    changes: dict
    user_id: uuid.UUID | None
    user_name: str | None = None
    created_at: datetime
