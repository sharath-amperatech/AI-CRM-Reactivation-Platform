from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

from celery.utils.log import get_task_logger

from app.tasks.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(
    name="app.tasks.embedding_tasks.embed_activities_batch",
    queue="embeddings",
    max_retries=3,
    default_retry_delay=30,
)
def embed_activities_batch(activity_ids: list[str], org_id: str) -> dict:
    """Embed a batch of CRM activity texts and store vectors in the DB."""
    logger.info("embedding_task_start", count=len(activity_ids))

    async def _run():
        from app.db.base import get_session_factory
        from app.services.embedding_service import EmbeddingService

        factory = get_session_factory()
        async with factory() as db:
            svc = EmbeddingService(db)
            uuids = [uuid.UUID(aid) for aid in activity_ids]
            results = await svc.embed_activities_batch(uuids)
            await db.commit()
            return len(results)

    try:
        count = asyncio.run(_run())
        logger.info("embedding_task_complete", embedded=count)
        return {"embedded": count}
    except Exception as exc:
        logger.error("embedding_task_failed", error=str(exc))
        raise


@celery_app.task(
    name="app.tasks.embedding_tasks.reindex_org_activities",
    queue="embeddings",
)
def reindex_org_activities(org_id: str, embedding_version_id: str) -> dict:
    """Full re-embedding of all CRM activities for an org (when switching models)."""
    logger.info("reindex_start", org_id=org_id)

    async def _run():
        from sqlalchemy import select
        from app.db.base import get_session_factory
        from app.models.crm_activity import CRMActivity
        from app.services.embedding_service import EmbeddingService

        factory = get_session_factory()
        async with factory() as db:
            result = await db.execute(
                select(CRMActivity.id).where(
                    CRMActivity.org_id == uuid.UUID(org_id)
                ).limit(1000)
            )
            activity_ids = [row[0] for row in result.fetchall()]

            if not activity_ids:
                return 0

            svc = EmbeddingService(db)
            results = await svc.embed_activities_batch(activity_ids)
            await db.commit()
            return len(results)

    count = asyncio.run(_run())
    logger.info("reindex_complete", org_id=org_id, count=count)
    return {"count": count}
