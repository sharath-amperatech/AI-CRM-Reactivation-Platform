from __future__ import annotations

import asyncio
import uuid

from celery.utils.log import get_task_logger

from app.tasks.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(
    name="app.tasks.evaluation_tasks.run_ragas_evaluation",
    queue="default",
)
def run_ragas_evaluation(org_id: str, num_samples: int = 50) -> dict:
    """Run RAGAS evaluation for an org and persist scores."""
    logger.info("ragas_task_start", org_id=org_id, num_samples=num_samples)

    async def _run():
        from app.db.base import get_session_factory
        from app.services.evaluation_service import EvaluationService

        factory = get_session_factory()
        async with factory() as db:
            svc = EvaluationService(db)
            run = await svc.run_evaluation(
                org_id=uuid.UUID(org_id),
                num_samples=num_samples,
                triggered_by="celery_task",
            )
            await db.commit()
            return {
                "run_id": str(run.id),
                "status": run.status,
                "faithfulness": run.faithfulness,
                "answer_relevancy": run.answer_relevancy,
            }

    result = asyncio.run(_run())
    logger.info("ragas_task_complete", **result)
    return result


@celery_app.task(name="app.tasks.evaluation_tasks.run_nightly_evaluation", queue="default")
def run_nightly_evaluation() -> dict:
    """Beat-scheduled: run nightly evaluations for all orgs."""
    logger.info("nightly_evaluation_start")

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
        run_ragas_evaluation.delay(org_id=org_id, num_samples=50)

    return {"dispatched": len(org_ids)}
