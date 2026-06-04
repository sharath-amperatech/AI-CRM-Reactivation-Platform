from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.models.approval import Approval, ApprovalStatus
from app.models.campaign import Campaign, CampaignStatus
from app.models.campaign_enrollment import CampaignEnrollment
from app.models.lead import Lead, LeadStatus
from app.schemas.campaign import CampaignCreate, CampaignUpdate

logger = get_logger(__name__)


class CampaignService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_campaigns(
        self,
        org_id: uuid.UUID,
        status: CampaignStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Campaign], int]:
        q = select(Campaign).where(Campaign.org_id == org_id)
        if status:
            q = q.where(Campaign.status == status)

        count_q = select(func.count()).select_from(q.subquery())
        total = (await self._db.execute(count_q)).scalar_one()

        q = q.order_by(Campaign.created_at.desc()).offset(skip).limit(limit)
        result = await self._db.execute(q)
        return list(result.scalars().all()), total

    async def get_campaign(self, campaign_id: uuid.UUID, org_id: uuid.UUID) -> Campaign:
        result = await self._db.execute(
            select(Campaign).where(Campaign.id == campaign_id, Campaign.org_id == org_id)
        )
        campaign = result.scalar_one_or_none()
        if campaign is None:
            raise NotFoundError("Campaign", str(campaign_id))
        return campaign

    async def create_campaign(
        self, org_id: uuid.UUID, data: CampaignCreate
    ) -> Campaign:
        campaign = Campaign(org_id=org_id, **data.model_dump())
        self._db.add(campaign)
        await self._db.flush()
        await self._db.refresh(campaign)
        logger.info("campaign_created", campaign_id=str(campaign.id))
        return campaign

    async def update_campaign(
        self, campaign_id: uuid.UUID, org_id: uuid.UUID, updates: CampaignUpdate
    ) -> Campaign:
        campaign = await self.get_campaign(campaign_id, org_id)
        for field, value in updates.model_dump(exclude_none=True).items():
            setattr(campaign, field, value)
        await self._db.flush()
        await self._db.refresh(campaign)
        return campaign

    async def pause(self, campaign_id: uuid.UUID, org_id: uuid.UUID) -> Campaign:
        campaign = await self.get_campaign(campaign_id, org_id)
        if campaign.status != CampaignStatus.ACTIVE:
            raise ConflictError(f"Campaign is not active (status={campaign.status})")
        campaign.status = CampaignStatus.PAUSED
        await self._db.flush()
        await self._db.refresh(campaign)
        logger.info("campaign_paused", campaign_id=str(campaign_id))
        return campaign

    async def resume(self, campaign_id: uuid.UUID, org_id: uuid.UUID) -> Campaign:
        campaign = await self.get_campaign(campaign_id, org_id)
        if campaign.status != CampaignStatus.PAUSED:
            raise ConflictError(f"Campaign is not paused (status={campaign.status})")
        campaign.status = CampaignStatus.ACTIVE
        if campaign.started_at is None:
            campaign.started_at = datetime.now(timezone.utc)
        await self._db.flush()
        await self._db.refresh(campaign)
        logger.info("campaign_resumed", campaign_id=str(campaign_id))
        return campaign

    async def launch(self, campaign_id: uuid.UUID, org_id: uuid.UUID) -> Campaign:
        campaign = await self.get_campaign(campaign_id, org_id)
        if campaign.status != CampaignStatus.DRAFT:
            raise ConflictError("Only draft campaigns can be launched")
        campaign.status = CampaignStatus.ACTIVE
        campaign.started_at = datetime.now(timezone.utc)
        await self._db.flush()

        enrolled_lead_ids = await self._enroll_matching_leads(campaign, org_id)
        await self._db.flush()

        await self._db.refresh(campaign)
        logger.info("campaign_launched", campaign_id=str(campaign_id), enrolled=len(enrolled_lead_ids))

        from app.tasks.workflow_tasks import trigger_reactivation_workflow
        for lead_id in enrolled_lead_ids:
            trigger_reactivation_workflow.delay(str(lead_id), str(campaign.id), str(org_id))

        return campaign

    async def _enroll_matching_leads(
        self, campaign: Campaign, org_id: uuid.UUID
    ) -> list[uuid.UUID]:
        q = select(Lead).where(
            Lead.org_id == org_id,
            Lead.status == LeadStatus.DORMANT,
            Lead.deleted_at.is_(None),
        )
        if campaign.segment != "all":
            q = q.where(Lead.segment == campaign.segment)

        result = await self._db.execute(q)
        leads = result.scalars().all()

        if not leads:
            return []

        existing_result = await self._db.execute(
            select(CampaignEnrollment.lead_id).where(
                CampaignEnrollment.campaign_id == campaign.id
            )
        )
        already_enrolled = {row for row in existing_result.scalars().all()}

        now = datetime.now(timezone.utc)
        new_enrollments = []
        for lead in leads:
            if lead.id in already_enrolled:
                continue
            new_enrollments.append(
                CampaignEnrollment(
                    org_id=org_id,
                    campaign_id=campaign.id,
                    lead_id=lead.id,
                    enrolled_at=now,
                )
            )

        if new_enrollments:
            self._db.add_all(new_enrollments)
            campaign.enrolled_leads += len(new_enrollments)
            logger.info(
                "leads_enrolled",
                campaign_id=str(campaign.id),
                count=len(new_enrollments),
            )

        return [e.lead_id for e in new_enrollments]

    async def list_enrollments(
        self, campaign_id: uuid.UUID, org_id: uuid.UUID
    ) -> list[CampaignEnrollment]:
        await self.get_campaign(campaign_id, org_id)
        result = await self._db.execute(
            select(CampaignEnrollment)
            .where(CampaignEnrollment.campaign_id == campaign_id)
            .options(selectinload(CampaignEnrollment.lead))
            .order_by(CampaignEnrollment.enrolled_at.desc())
        )
        return list(result.scalars().all())

    async def get_campaign_approvals(
        self, campaign_id: uuid.UUID, org_id: uuid.UUID
    ) -> list[Approval]:
        await self.get_campaign(campaign_id, org_id)
        result = await self._db.execute(
            select(Approval)
            .where(Approval.campaign_id == campaign_id, Approval.org_id == org_id)
            .order_by(Approval.created_at.desc())
        )
        return list(result.scalars().all())

    async def enroll_lead(
        self, campaign_id: uuid.UUID, lead_id: uuid.UUID, org_id: uuid.UUID
    ) -> CampaignEnrollment:
        existing = await self._db.execute(
            select(CampaignEnrollment).where(
                CampaignEnrollment.campaign_id == campaign_id,
                CampaignEnrollment.lead_id == lead_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError("Lead is already enrolled in this campaign")

        enrollment = CampaignEnrollment(
            org_id=org_id,
            campaign_id=campaign_id,
            lead_id=lead_id,
            enrolled_at=datetime.now(timezone.utc),
        )
        self._db.add(enrollment)

        campaign = await self.get_campaign(campaign_id, org_id)
        campaign.enrolled_leads += 1
        await self._db.flush()
        logger.info("lead_enrolled", campaign_id=str(campaign_id), lead_id=str(lead_id))
        return enrollment
