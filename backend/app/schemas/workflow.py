from __future__ import annotations

import uuid

from pydantic import Field

from app.schemas.common import APIModel


class WorkflowTriggerRequest(APIModel):
    lead_id: uuid.UUID
    campaign_id: uuid.UUID


class WorkflowStatus(APIModel):
    thread_id: str
    lead_id: str
    campaign_id: str
    status: str
    current_node: str | None = None
    error: str | None = None
    metadata: dict = Field(default_factory=dict)


class WorkflowResumeRequest(APIModel):
    thread_id: str
    approval_status: str
