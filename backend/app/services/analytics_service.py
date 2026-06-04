from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.approval import Approval, ApprovalStatus
from app.models.booking import Booking
from app.models.campaign import Campaign, CampaignStatus
from app.models.lead import Lead, LeadStatus
from app.models.message import Message
from app.schemas.analytics import (
    CampaignMetric,
    DashboardKPIs,
    DashboardResponse,
    DataPoint,
    FunnelData,
    FunnelStage,
    SegmentMetric,
)

logger = get_logger(__name__)


class AnalyticsService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_dashboard(self, org_id: uuid.UUID) -> DashboardResponse:
        kpis = await self._get_kpis(org_id)
        trend = await self._get_revenue_trend(org_id, days=30)
        perf = await self._get_campaign_performance(org_id)
        return DashboardResponse(kpis=kpis, revenue_trend=trend, campaign_performance=perf)

    async def _get_kpis(self, org_id: uuid.UUID) -> DashboardKPIs:
        revenue = (await self._db.execute(
            select(func.sum(Lead.deal_value)).where(
                Lead.org_id == org_id,
                Lead.status == LeadStatus.REACTIVATED,
                Lead.deleted_at.is_(None),
            )
        )).scalar_one() or 0.0

        active_leads = (await self._db.execute(
            select(func.count()).where(
                Lead.org_id == org_id,
                Lead.status.in_([LeadStatus.ACTIVE, LeadStatus.DORMANT]),
                Lead.deleted_at.is_(None),
            )
        )).scalar_one()

        meetings = (await self._db.execute(
            select(func.count()).where(Booking.org_id == org_id)
        )).scalar_one()

        active_campaigns = (await self._db.execute(
            select(func.count()).where(
                Campaign.org_id == org_id,
                Campaign.status == CampaignStatus.ACTIVE,
            )
        )).scalar_one()

        pending_approvals = (await self._db.execute(
            select(func.count()).where(
                Approval.org_id == org_id,
                Approval.status == ApprovalStatus.PENDING,
            )
        )).scalar_one()

        ai_messages = (await self._db.execute(
            select(func.count()).where(Message.org_id == org_id)
        )).scalar_one()

        return DashboardKPIs(
            revenue_recovered=float(revenue),
            active_leads=active_leads,
            meetings_booked=meetings,
            active_campaigns=active_campaigns,
            pending_approvals=pending_approvals,
            ai_messages_generated=ai_messages,
        )

    async def _get_revenue_trend(
        self, org_id: uuid.UUID, days: int = 30
    ) -> list[DataPoint]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self._db.execute(
            select(
                func.date_trunc("day", Lead.updated_at).label("day"),
                func.sum(Lead.deal_value).label("revenue"),
            )
            .where(
                Lead.org_id == org_id,
                Lead.status == LeadStatus.REACTIVATED,
                Lead.updated_at >= since,
                Lead.deleted_at.is_(None),
            )
            .group_by("day")
            .order_by("day")
        )
        return [
            DataPoint(date=str(row.day.date()), value=float(row.revenue))
            for row in result.fetchall()
        ]

    async def _get_campaign_performance(self, org_id: uuid.UUID) -> list[dict]:
        result = await self._db.execute(
            select(Campaign).where(Campaign.org_id == org_id)
            .order_by(Campaign.revenue_recovered.desc())
            .limit(10)
        )
        campaigns = result.scalars().all()
        return [
            {
                "campaign_id": str(c.id),
                "name": c.name,
                "enrolled_leads": c.enrolled_leads,
                "open_rate": c.open_rate,
                "reply_rate": c.reply_rate,
                "meetings_booked": c.meetings_booked,
                "revenue_recovered": c.revenue_recovered,
            }
            for c in campaigns
        ]

    async def get_funnel(
        self, org_id: uuid.UUID, campaign_id: uuid.UUID | None = None
    ) -> FunnelData:
        dormant = (await self._db.execute(
            select(func.count()).where(Lead.org_id == org_id, Lead.status == LeadStatus.DORMANT, Lead.deleted_at.is_(None))
        )).scalar_one()

        active = (await self._db.execute(
            select(func.count()).where(Lead.org_id == org_id, Lead.status == LeadStatus.ACTIVE, Lead.deleted_at.is_(None))
        )).scalar_one()

        meetings = (await self._db.execute(
            select(func.count()).where(Lead.org_id == org_id, Lead.status == LeadStatus.MEETING_BOOKED, Lead.deleted_at.is_(None))
        )).scalar_one()

        reactivated = (await self._db.execute(
            select(func.count()).where(Lead.org_id == org_id, Lead.status == LeadStatus.REACTIVATED, Lead.deleted_at.is_(None))
        )).scalar_one()

        return FunnelData(
            stages=[
                FunnelStage(stage="dormant", count=dormant),
                FunnelStage(stage="active", count=active),
                FunnelStage(stage="meeting_booked", count=meetings),
                FunnelStage(stage="reactivated", count=reactivated),
            ]
        )

    async def get_segment_metrics(self, org_id: uuid.UUID) -> list[SegmentMetric]:
        result = await self._db.execute(
            select(
                Lead.segment,
                func.count(Lead.id).label("count"),
                func.sum(Lead.deal_value).label("revenue"),
                func.avg(Lead.confidence).label("avg_conf"),
            )
            .where(Lead.org_id == org_id, Lead.deleted_at.is_(None))
            .group_by(Lead.segment)
        )
        rows = result.fetchall()
        return [
            SegmentMetric(
                segment=str(row.segment),
                lead_count=row.count,
                revenue_recovered=float(row.revenue or 0),
                avg_confidence=float(row.avg_conf or 0),
                meetings_booked=0,
            )
            for row in rows
        ]
