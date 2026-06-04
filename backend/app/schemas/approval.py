from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import Field

from app.models.approval import ApprovalStatus
from app.schemas.common import APIModel


class ApprovalRead(APIModel):
    id: uuid.UUID
    org_id: uuid.UUID
    message_id: uuid.UUID
    lead_id: uuid.UUID
    campaign_id: uuid.UUID | None
    status: ApprovalStatus
    confidence: float
    crm_context: str | None
    ai_reasoning: str | None
    retrieved_chunks: list
    trace_id: str | None
    approved_by_id: uuid.UUID | None
    approved_at: datetime | None
    edited_body: str | None
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime

    # Denormalized from joins (populated by service)
    lead_name: str | None = None
    company: str | None = None
    segment: str | None = None
    deal_value: float | None = None
    campaign_name: str | None = None
    message_subject: str | None = None
    message_body: str | None = None
    channel: str | None = None


class ApprovalApprove(APIModel):
    pass


class ApprovalReject(APIModel):
    reason: str | None = None


class ApprovalEdit(APIModel):
    edited_body: str


class BulkApproveRequest(APIModel):
    confidence_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
