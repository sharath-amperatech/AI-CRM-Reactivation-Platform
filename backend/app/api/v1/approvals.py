from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, get_current_user, get_org_id
from app.db.session import get_db
from app.models.user import User
from app.schemas.approval import (
    ApprovalEdit,
    ApprovalRead,
    ApprovalReject,
    BulkApproveRequest,
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/approvals", tags=["approvals"])


def _get_approval_svc(db: AsyncSession = Depends(get_db)) -> ApprovalService:
    return ApprovalService(db=db, audit=AuditService(db))


@router.get("", response_model=PaginatedResponse[ApprovalRead])
async def list_approvals(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    org_id: uuid.UUID = Depends(get_org_id),
    svc: ApprovalService = Depends(_get_approval_svc),
):
    skip = (page - 1) * page_size
    approvals, total = await svc.list_pending(org_id=org_id, skip=skip, limit=page_size)
    pages = (total + page_size - 1) // page_size
    return PaginatedResponse(items=approvals, total=total, page=page, page_size=page_size, pages=pages)


@router.post("/{approval_id}/approve", response_model=ApprovalRead)
async def approve(
    approval_id: uuid.UUID,
    org_id: uuid.UUID = Depends(get_org_id),
    user: User = Depends(get_current_user),
    svc: ApprovalService = Depends(_get_approval_svc),
):
    return await svc.approve(approval_id=approval_id, org_id=org_id, user=user)


@router.post("/{approval_id}/reject", response_model=ApprovalRead)
async def reject(
    approval_id: uuid.UUID,
    body: ApprovalReject,
    org_id: uuid.UUID = Depends(get_org_id),
    user: User = Depends(get_current_user),
    svc: ApprovalService = Depends(_get_approval_svc),
):
    return await svc.reject(
        approval_id=approval_id, org_id=org_id, user=user, reason=body.reason
    )


@router.post("/{approval_id}/edit", response_model=ApprovalRead)
async def edit_and_approve(
    approval_id: uuid.UUID,
    body: ApprovalEdit,
    org_id: uuid.UUID = Depends(get_org_id),
    user: User = Depends(get_current_user),
    svc: ApprovalService = Depends(_get_approval_svc),
):
    return await svc.edit_and_approve(
        approval_id=approval_id, org_id=org_id, user=user, edited_body=body.edited_body
    )


@router.post("/bulk-approve", response_model=SuccessResponse)
async def bulk_approve(
    body: BulkApproveRequest,
    org_id: uuid.UUID = Depends(get_org_id),
    user: User = Depends(get_current_user),
    svc: ApprovalService = Depends(_get_approval_svc),
):
    count = await svc.bulk_approve_high_confidence(
        org_id=org_id,
        user=user,
        confidence_threshold=body.confidence_threshold,
    )
    return SuccessResponse(message=f"Approved {count} messages")
