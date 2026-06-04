from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, get_org_id
from app.db.session import get_db
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/integrations", tags=["integrations"])

INTEGRATION_REGISTRY = {
    "hubspot": {"name": "HubSpot", "description": "CRM contact and activity sync"},
    "resend": {"name": "Resend", "description": "Transactional email delivery"},
    "twilio": {"name": "Twilio", "description": "SMS messaging"},
    "calendly": {"name": "Calendly", "description": "Meeting booking"},
}


@router.get("")
async def list_integrations(
    org_id: uuid.UUID = Depends(get_org_id),
):
    integrations = []
    for key, meta in INTEGRATION_REGISTRY.items():
        integrations.append({
            "id": key,
            "name": meta["name"],
            "description": meta["description"],
            "connected": False,  # TODO: check org settings
            "last_sync": None,
        })
    return integrations


@router.post("/{integration_id}/connect")
async def connect_integration(
    integration_id: str,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    if integration_id not in INTEGRATION_REGISTRY:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Integration '{integration_id}' not found")
    # Placeholder — implement OAuth / API key storage per integration
    return SuccessResponse(message=f"{integration_id} connection initiated")


@router.post("/{integration_id}/sync")
async def sync_integration(
    integration_id: str,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    if integration_id == "hubspot":
        from app.tasks.hubspot_tasks import sync_hubspot_contacts
        sync_hubspot_contacts.delay(org_id=str(org_id))
        return SuccessResponse(message="HubSpot sync queued")
    return SuccessResponse(message=f"{integration_id} sync not yet implemented")
