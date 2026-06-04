from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, get_org_id
from app.db.session import get_db
from app.schemas.approval import ApprovalRead
from app.schemas.campaign import CampaignCreate, CampaignEnrollmentRead, CampaignRead, CampaignUpdate
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=PaginatedResponse[CampaignRead])
async def list_campaigns(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    from app.models.campaign import CampaignStatus as CS
    svc = CampaignService(db)
    skip = (page - 1) * page_size
    campaigns, total = await svc.list_campaigns(
        org_id=org_id,
        status=CS(status) if status else None,
        skip=skip,
        limit=page_size,
    )
    pages = (total + page_size - 1) // page_size
    return PaginatedResponse(items=campaigns, total=total, page=page, page_size=page_size, pages=pages)


@router.post("", response_model=CampaignRead, status_code=201)
async def create_campaign(
    data: CampaignCreate,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = CampaignService(db)
    return await svc.create_campaign(org_id=org_id, data=data)


@router.get("/{campaign_id}", response_model=CampaignRead)
async def get_campaign(
    campaign_id: uuid.UUID,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = CampaignService(db)
    return await svc.get_campaign(campaign_id=campaign_id, org_id=org_id)


@router.put("/{campaign_id}", response_model=CampaignRead)
async def update_campaign(
    campaign_id: uuid.UUID,
    updates: CampaignUpdate,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = CampaignService(db)
    return await svc.update_campaign(campaign_id=campaign_id, org_id=org_id, updates=updates)


@router.post("/{campaign_id}/pause", response_model=CampaignRead)
async def pause_campaign(
    campaign_id: uuid.UUID,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = CampaignService(db)
    return await svc.pause(campaign_id=campaign_id, org_id=org_id)


@router.post("/{campaign_id}/resume", response_model=CampaignRead)
async def resume_campaign(
    campaign_id: uuid.UUID,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = CampaignService(db)
    return await svc.resume(campaign_id=campaign_id, org_id=org_id)


@router.post("/{campaign_id}/launch", response_model=CampaignRead)
async def launch_campaign(
    campaign_id: uuid.UUID,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = CampaignService(db)
    return await svc.launch(campaign_id=campaign_id, org_id=org_id)


@router.get("/{campaign_id}/enrollments", response_model=list[CampaignEnrollmentRead])
async def list_campaign_enrollments(
    campaign_id: uuid.UUID,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = CampaignService(db)
    return await svc.list_enrollments(campaign_id=campaign_id, org_id=org_id)


@router.get("/{campaign_id}/approvals", response_model=list[ApprovalRead])
async def get_campaign_approvals(
    campaign_id: uuid.UUID,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = CampaignService(db)
    return await svc.get_campaign_approvals(campaign_id=campaign_id, org_id=org_id)
