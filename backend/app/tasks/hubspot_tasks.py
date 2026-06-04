from __future__ import annotations

import asyncio

from celery.utils.log import get_task_logger

from app.tasks.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(
    name="app.tasks.hubspot_tasks.sync_hubspot_contacts",
    queue="default",
    max_retries=2,
)
def sync_hubspot_contacts(org_id: str) -> dict:
    """Sync HubSpot contacts for a single org."""
    logger.info("hubspot_sync_task_start", org_id=org_id)

    async def _run():
        from app.db.base import get_session_factory
        from app.services.hubspot_service import HubSpotService

        factory = get_session_factory()
        async with factory() as db:
            svc = HubSpotService(db)
            result = await svc.sync_contacts(org_id=org_id)
            await db.commit()
            return result

    try:
        result = asyncio.run(_run())
        logger.info("hubspot_sync_task_complete", org_id=org_id, **result)
        return result
    except Exception as exc:
        logger.error("hubspot_sync_task_failed", org_id=org_id, error=str(exc))
        raise


@celery_app.task(name="app.tasks.hubspot_tasks.sync_all_orgs", queue="default")
def sync_all_orgs() -> dict:
    """Beat-scheduled: sync all active orgs from HubSpot."""
    logger.info("hubspot_sync_all_orgs_start")

    async def _get_org_ids():
        from sqlalchemy import select
        from app.db.base import get_session_factory
        from app.models.organization import Organization

        factory = get_session_factory()
        async with factory() as db:
            result = await db.execute(
                select(Organization.id).where(Organization.is_active == True)
            )
            return [str(row[0]) for row in result.fetchall()]

    org_ids = asyncio.run(_get_org_ids())
    for org_id in org_ids:
        sync_hubspot_contacts.delay(org_id=org_id)

    logger.info("hubspot_sync_all_dispatched", count=len(org_ids))
    return {"dispatched": len(org_ids)}
