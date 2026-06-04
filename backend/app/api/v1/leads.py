from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, get_org_id
from app.db.session import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.lead import AuditLogRead, CRMActivityRead, LeadFilter, LeadListRead, LeadMessageRead, LeadRead, LeadUpdate
from app.services.lead_service import LeadService

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=PaginatedResponse[LeadListRead])
async def list_leads(
    segment: str | None = Query(None),
    status: str | None = Query(None),
    search: str | None = Query(None),
    min_deal_value: float | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    from app.models.lead import LeadSegment, LeadStatus as LS

    filters = LeadFilter(
        segment=LeadSegment(segment) if segment else None,
        status=LS(status) if status else None,
        search=search,
        min_deal_value=min_deal_value,
    )
    svc = LeadService(db)
    skip = (page - 1) * page_size
    leads, total = await svc.list_leads(org_id=org_id, filters=filters, skip=skip, limit=page_size)
    pages = (total + page_size - 1) // page_size
    return PaginatedResponse(items=leads, total=total, page=page, page_size=page_size, pages=pages)


@router.get("/{lead_id}", response_model=LeadRead)
async def get_lead(
    lead_id: uuid.UUID,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = LeadService(db)
    return await svc.get_lead(lead_id=lead_id, org_id=org_id)


@router.put("/{lead_id}", response_model=LeadRead)
async def update_lead(
    lead_id: uuid.UUID,
    updates: LeadUpdate,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = LeadService(db)
    return await svc.update_lead(lead_id=lead_id, org_id=org_id, updates=updates)


@router.get("/{lead_id}/activities", response_model=list[CRMActivityRead])
async def get_lead_activities(
    lead_id: uuid.UUID,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = LeadService(db)
    return await svc.get_activities(lead_id=lead_id, org_id=org_id)


@router.get("/{lead_id}/messages", response_model=list[LeadMessageRead])
async def get_lead_messages(
    lead_id: uuid.UUID,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = LeadService(db)
    return await svc.get_messages(lead_id=lead_id, org_id=org_id)


@router.get("/{lead_id}/audit", response_model=list[AuditLogRead])
async def get_lead_audit(
    lead_id: uuid.UUID,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = LeadService(db)
    return await svc.get_audit_logs(lead_id=lead_id, org_id=org_id)
