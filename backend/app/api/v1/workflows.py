from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, get_org_id
from app.db.session import get_db
from app.schemas.workflow import WorkflowStatus, WorkflowTriggerRequest

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/trigger", response_model=WorkflowStatus, status_code=202)
async def trigger_workflow(
    body: WorkflowTriggerRequest,
    org_id: uuid.UUID = Depends(get_org_id),
):
    from app.tasks.workflow_tasks import trigger_reactivation_workflow
    thread_id = f"{body.campaign_id}:{body.lead_id}"
    trigger_reactivation_workflow.delay(
        lead_id=str(body.lead_id),
        campaign_id=str(body.campaign_id),
        org_id=str(org_id),
    )
    return WorkflowStatus(
        thread_id=thread_id,
        lead_id=str(body.lead_id),
        campaign_id=str(body.campaign_id),
        status="queued",
        current_node="fetch_lead",
    )


@router.get("/{thread_id}/status", response_model=WorkflowStatus)
async def get_workflow_status(
    thread_id: str,
    org_id: uuid.UUID = Depends(get_org_id),
):
    # Placeholder — implement checkpoint lookup from Redis/DB
    parts = thread_id.split(":")
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid thread_id format")
    campaign_id, lead_id = parts
    return WorkflowStatus(
        thread_id=thread_id,
        lead_id=lead_id,
        campaign_id=campaign_id,
        status="unknown",
    )
