from __future__ import annotations

from pydantic import Field

from app.schemas.common import APIModel


class DataPoint(APIModel):
    date: str
    value: float


class KPICard(APIModel):
    label: str
    value: float | int | str
    change_pct: float | None = None
    trend: str | None = None


class DashboardKPIs(APIModel):
    revenue_recovered: float
    active_leads: int
    meetings_booked: int
    active_campaigns: int
    pending_approvals: int
    ai_messages_generated: int
    cache_hit_rate: float | None = None
    avg_latency_ms: float | None = None
    ai_cost_mtd: float | None = None


class DashboardResponse(APIModel):
    kpis: DashboardKPIs
    revenue_trend: list[DataPoint]
    campaign_performance: list[dict]


class FunnelStage(APIModel):
    stage: str
    count: int
    conversion_rate: float | None = None


class FunnelData(APIModel):
    stages: list[FunnelStage]
    campaign_id: str | None = None


class SegmentMetric(APIModel):
    segment: str
    lead_count: int
    revenue_recovered: float
    avg_confidence: float
    meetings_booked: int


class CampaignMetric(APIModel):
    campaign_id: str
    campaign_name: str
    enrolled_leads: int
    open_rate: float
    reply_rate: float
    meetings_booked: int
    revenue_recovered: float


class SDRLeaderboardEntry(APIModel):
    user_id: str
    name: str
    leads_worked: int
    meetings_booked: int
    revenue_recovered: float
