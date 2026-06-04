from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, get_org_id
from app.db.session import get_db
from app.schemas.analytics import DashboardResponse, FunnelData, SegmentMetric
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = AnalyticsService(db)
    return await svc.get_dashboard(org_id=org_id)


@router.get("/funnel", response_model=FunnelData)
async def get_funnel(
    campaign_id: uuid.UUID | None = Query(None),
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = AnalyticsService(db)
    return await svc.get_funnel(org_id=org_id, campaign_id=campaign_id)


@router.get("/segments", response_model=list[SegmentMetric])
async def get_segment_metrics(
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = AnalyticsService(db)
    return await svc.get_segment_metrics(org_id=org_id)


@router.get("/campaigns", response_model=list[dict])
async def get_campaign_performance(
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = AnalyticsService(db)
    dashboard = await svc.get_dashboard(org_id=org_id)
    return dashboard.campaign_performance
