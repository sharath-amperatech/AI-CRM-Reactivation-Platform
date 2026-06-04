from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.approval import Approval
from app.models.audit_log import AuditLog
from app.models.crm_activity import CRMActivity
from app.models.campaign_enrollment import CampaignEnrollment
from app.models.lead import Lead, LeadSegment, LeadStatus
from app.models.message import Message
from app.schemas.lead import AuditLogRead, LeadFilter, LeadMessageRead, LeadUpdate

logger = get_logger(__name__)


class LeadService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_leads(
        self,
        org_id: uuid.UUID,
        filters: LeadFilter,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Lead], int]:
        q = select(Lead).where(Lead.org_id == org_id, Lead.deleted_at.is_(None))

        if filters.segment:
            q = q.where(Lead.segment == filters.segment)
        if filters.status:
            q = q.where(Lead.status == filters.status)
        if filters.assigned_to_id:
            q = q.where(Lead.assigned_to_id == filters.assigned_to_id)
        if filters.search:
            pattern = f"%{filters.search}%"
            q = q.where(Lead.name.ilike(pattern) | Lead.company.ilike(pattern) | Lead.email.ilike(pattern))
        if filters.min_deal_value is not None:
            q = q.where(Lead.deal_value >= filters.min_deal_value)
        if filters.min_inactive_days is not None:
            q = q.where(Lead.inactive_days >= filters.min_inactive_days)

        count_q = select(func.count()).select_from(q.subquery())
        total = (await self._db.execute(count_q)).scalar_one()

        q = q.order_by(Lead.inactive_days.desc()).offset(skip).limit(limit)
        result = await self._db.execute(q)
        leads = result.scalars().all()

        return list(leads), total

    async def get_lead(self, lead_id: uuid.UUID, org_id: uuid.UUID) -> Lead:
        result = await self._db.execute(
            select(Lead)
            .where(
                Lead.id == lead_id,
                Lead.org_id == org_id,
                Lead.deleted_at.is_(None),
            )
            .options(selectinload(Lead.enrollments).selectinload(CampaignEnrollment.campaign))
        )
        lead = result.scalar_one_or_none()
        if lead is None:
            raise NotFoundError("Lead", str(lead_id))
        return lead

    async def update_lead(
        self, lead_id: uuid.UUID, org_id: uuid.UUID, updates: LeadUpdate
    ) -> Lead:
        lead = await self.get_lead(lead_id, org_id)
        for field, value in updates.model_dump(exclude_none=True).items():
            setattr(lead, field, value)
        await self._db.flush()
        logger.info("lead_updated", lead_id=str(lead_id))
        return lead

    async def soft_delete(self, lead_id: uuid.UUID, org_id: uuid.UUID) -> None:
        from datetime import datetime, timezone
        lead = await self.get_lead(lead_id, org_id)
        lead.deleted_at = datetime.now(timezone.utc)
        await self._db.flush()
        logger.info("lead_deleted", lead_id=str(lead_id))

    async def get_activities(
        self, lead_id: uuid.UUID, org_id: uuid.UUID
    ) -> list[CRMActivity]:
        await self.get_lead(lead_id, org_id)  # verify access
        result = await self._db.execute(
            select(CRMActivity)
            .where(CRMActivity.lead_id == lead_id, CRMActivity.org_id == org_id)
            .order_by(CRMActivity.occurred_at.desc())
        )
        return list(result.scalars().all())

    async def get_dormant_leads(
        self,
        org_id: uuid.UUID,
        min_inactive_days: int = 30,
        limit: int = 100,
    ) -> list[Lead]:
        result = await self._db.execute(
            select(Lead)
            .where(
                Lead.org_id == org_id,
                Lead.status == LeadStatus.DORMANT,
                Lead.inactive_days >= min_inactive_days,
                Lead.deleted_at.is_(None),
            )
            .order_by(Lead.deal_value.desc(), Lead.inactive_days.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_messages(
        self, lead_id: uuid.UUID, org_id: uuid.UUID
    ) -> list[LeadMessageRead]:
        await self.get_lead(lead_id, org_id)
        result = await self._db.execute(
            select(Message)
            .where(Message.lead_id == lead_id, Message.org_id == org_id)
            .options(selectinload(Message.approval))
            .order_by(Message.created_at.desc())
        )
        out = []
        for msg in result.scalars().all():
            a = msg.approval
            out.append(LeadMessageRead(
                id=msg.id,
                channel=msg.channel,
                subject=msg.subject,
                body=msg.body,
                status=msg.status.value,
                sent_at=msg.sent_at,
                created_at=msg.created_at,
                approval_id=a.id if a else None,
                confidence=a.confidence if a else 0.0,
                ai_reasoning=a.ai_reasoning if a else None,
                retrieved_chunks=a.retrieved_chunks if a else [],
                trace_id=a.trace_id if a else None,
                approval_status=a.status.value if a else None,
            ))
        return out

    async def get_audit_logs(
        self, lead_id: uuid.UUID, org_id: uuid.UUID
    ) -> list[AuditLogRead]:
        from sqlalchemy import String as SAString, cast, or_
        from app.models.user import User

        await self.get_lead(lead_id, org_id)

        msg_ids = select(cast(Message.id, SAString)).where(
            Message.lead_id == lead_id, Message.org_id == org_id
        ).scalar_subquery()
        appr_ids = select(cast(Approval.id, SAString)).where(
            Approval.lead_id == lead_id, Approval.org_id == org_id
        ).scalar_subquery()

        q = (
            select(AuditLog, User.name.label("user_name"))
            .outerjoin(User, AuditLog.user_id == User.id)
            .where(
                AuditLog.org_id == org_id,
                or_(
                    (AuditLog.resource_type == "lead") & (AuditLog.resource_id == str(lead_id)),
                    (AuditLog.resource_type == "message") & (AuditLog.resource_id.in_(msg_ids)),
                    (AuditLog.resource_type == "approval") & (AuditLog.resource_id.in_(appr_ids)),
                ),
            )
            .order_by(AuditLog.created_at.desc())
        )
        return [
            AuditLogRead(
                id=r.AuditLog.id,
                action=r.AuditLog.action,
                resource_type=r.AuditLog.resource_type,
                resource_id=r.AuditLog.resource_id,
                changes=r.AuditLog.changes or {},
                user_id=r.AuditLog.user_id,
                user_name=r.user_name,
                created_at=r.AuditLog.created_at,
            )
            for r in (await self._db.execute(q)).all()
        ]
