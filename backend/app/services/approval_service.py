from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import get_logger
from app.models.approval import Approval, ApprovalStatus
from app.models.message import Message, MessageStatus
from app.models.user import User
from app.schemas.approval import ApprovalRead
from app.services.audit_service import AuditService

logger = get_logger(__name__)

_LOAD_OPTS = (
    selectinload(Approval.lead),
    selectinload(Approval.message),
    selectinload(Approval.campaign),
)


class ApprovalService:
    def __init__(self, db: AsyncSession, audit: AuditService) -> None:
        self._db = db
        self._audit = audit

    @staticmethod
    def _enrich(a: Approval) -> ApprovalRead:
        lead = a.lead
        msg = a.message
        camp = a.campaign
        is_edited = a.status == ApprovalStatus.EDITED and a.edited_body
        return ApprovalRead(
            id=a.id,
            org_id=a.org_id,
            message_id=a.message_id,
            lead_id=a.lead_id,
            campaign_id=a.campaign_id,
            status=a.status,
            confidence=a.confidence,
            crm_context=a.crm_context,
            ai_reasoning=a.ai_reasoning,
            retrieved_chunks=a.retrieved_chunks or [],
            trace_id=a.trace_id,
            approved_by_id=a.approved_by_id,
            approved_at=a.approved_at,
            edited_body=a.edited_body,
            rejection_reason=a.rejection_reason,
            created_at=a.created_at,
            updated_at=a.updated_at,
            lead_name=lead.name if lead else None,
            company=lead.company if lead else None,
            segment=lead.segment if lead else None,
            deal_value=lead.deal_value if lead else None,
            campaign_name=camp.name if camp else None,
            message_subject=msg.subject if msg else None,
            message_body=a.edited_body if is_edited else (msg.body if msg else None),
            channel=msg.channel if msg else None,
        )

    async def list_pending(
        self,
        org_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[ApprovalRead], int]:
        q = select(Approval).where(
            Approval.org_id == org_id,
            Approval.status == ApprovalStatus.PENDING,
        )
        count_q = select(func.count()).select_from(q.subquery())
        total = (await self._db.execute(count_q)).scalar_one()

        q = (
            q.options(*_LOAD_OPTS)
            .order_by(Approval.confidence.desc(), Approval.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._db.execute(q)
        rows = list(result.scalars().all())
        return [self._enrich(a) for a in rows], total

    async def get_approval(self, approval_id: uuid.UUID, org_id: uuid.UUID) -> Approval:
        result = await self._db.execute(
            select(Approval).where(Approval.id == approval_id, Approval.org_id == org_id)
        )
        approval = result.scalar_one_or_none()
        if approval is None:
            raise NotFoundError("Approval", str(approval_id))
        return approval

    async def _get_with_relations(self, approval_id: uuid.UUID, org_id: uuid.UUID) -> Approval:
        result = await self._db.execute(
            select(Approval)
            .options(*_LOAD_OPTS)
            .where(Approval.id == approval_id, Approval.org_id == org_id)
        )
        approval = result.scalar_one_or_none()
        if approval is None:
            raise NotFoundError("Approval", str(approval_id))
        return approval

    async def approve(
        self, approval_id: uuid.UUID, org_id: uuid.UUID, user: User
    ) -> ApprovalRead:
        approval = await self._get_with_relations(approval_id, org_id)
        if approval.status != ApprovalStatus.PENDING:
            raise ConflictError(f"Approval is already {approval.status}")

        now = datetime.now(timezone.utc)
        approval.status = ApprovalStatus.APPROVED
        approval.approved_by_id = user.id
        approval.approved_at = now

        await self._update_message_status(approval.message_id, MessageStatus.APPROVED)
        await self._audit.log(
            org_id=org_id, user_id=user.id, action="approval.approved",
            resource_type="approval", resource_id=str(approval_id),
        )
        await self._notify_workflow(approval)
        await self._db.flush()
        logger.info("approval_approved", approval_id=str(approval_id), user_id=str(user.id))
        return self._enrich(approval)

    async def reject(
        self,
        approval_id: uuid.UUID,
        org_id: uuid.UUID,
        user: User,
        reason: str | None = None,
    ) -> ApprovalRead:
        approval = await self._get_with_relations(approval_id, org_id)
        if approval.status != ApprovalStatus.PENDING:
            raise ConflictError(f"Approval is already {approval.status}")

        approval.status = ApprovalStatus.REJECTED
        approval.approved_by_id = user.id
        approval.approved_at = datetime.now(timezone.utc)
        if reason:
            approval.rejection_reason = reason

        await self._update_message_status(approval.message_id, MessageStatus.REJECTED)
        await self._audit.log(
            org_id=org_id, user_id=user.id, action="approval.rejected",
            resource_type="approval", resource_id=str(approval_id),
        )
        await self._notify_workflow(approval)
        await self._db.flush()
        logger.info("approval_rejected", approval_id=str(approval_id))
        return self._enrich(approval)

    async def edit_and_approve(
        self,
        approval_id: uuid.UUID,
        org_id: uuid.UUID,
        user: User,
        edited_body: str,
    ) -> ApprovalRead:
        approval = await self._get_with_relations(approval_id, org_id)
        if approval.status != ApprovalStatus.PENDING:
            raise ConflictError(f"Approval is already {approval.status}")

        now = datetime.now(timezone.utc)
        approval.status = ApprovalStatus.EDITED
        approval.edited_body = edited_body
        approval.approved_by_id = user.id
        approval.approved_at = now

        # Update message body to the edited version
        msg_result = await self._db.execute(
            select(Message).where(Message.id == approval.message_id)
        )
        msg = msg_result.scalar_one_or_none()
        if msg:
            msg.body = edited_body
            msg.status = MessageStatus.APPROVED

        await self._audit.log(
            org_id=org_id, user_id=user.id, action="approval.edited",
            resource_type="approval", resource_id=str(approval_id),
            changes={"edited_body_length": len(edited_body)},
        )
        await self._notify_workflow(approval)
        await self._db.flush()
        logger.info("approval_edited", approval_id=str(approval_id))
        return self._enrich(approval)

    async def bulk_approve_high_confidence(
        self,
        org_id: uuid.UUID,
        user: User,
        confidence_threshold: float = 0.85,
    ) -> int:
        result = await self._db.execute(
            select(Approval).where(
                Approval.org_id == org_id,
                Approval.status == ApprovalStatus.PENDING,
                Approval.confidence >= confidence_threshold,
            )
        )
        approvals = result.scalars().all()
        now = datetime.now(timezone.utc)
        count = 0

        for approval in approvals:
            approval.status = ApprovalStatus.APPROVED
            approval.approved_by_id = user.id
            approval.approved_at = now
            await self._update_message_status(approval.message_id, MessageStatus.APPROVED)
            await self._notify_workflow(approval)
            count += 1

        await self._db.flush()
        logger.info("bulk_approve_complete", count=count, threshold=confidence_threshold)
        return count

    async def _update_message_status(
        self, message_id: uuid.UUID, status: MessageStatus
    ) -> None:
        result = await self._db.execute(
            select(Message).where(Message.id == message_id)
        )
        msg = result.scalar_one_or_none()
        if msg:
            msg.status = status

    async def _notify_workflow(self, approval: Approval) -> None:
        """Signal the LangGraph workflow that approval decision is ready."""
        try:
            from app.tasks.workflow_tasks import resume_workflow_after_approval
            thread_id = f"{approval.campaign_id}:{approval.lead_id}"
            resume_workflow_after_approval.delay(
                thread_id=thread_id,
                approval_status=approval.status.value,
            )
        except Exception as exc:
            logger.warning("workflow_notify_failed", error=str(exc))
