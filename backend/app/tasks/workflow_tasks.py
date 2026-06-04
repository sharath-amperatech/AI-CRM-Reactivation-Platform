from __future__ import annotations

import asyncio

from celery.utils.log import get_task_logger

from app.observability import configure_langfuse, flush_langfuse, observe
from app.tasks.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.workflow_tasks.trigger_reactivation_workflow",
    max_retries=3,
    default_retry_delay=60,
    queue="workflows",
)
def trigger_reactivation_workflow(
    self,
    lead_id: str,
    campaign_id: str,
    org_id: str,
) -> dict:
    """Trigger the full LangGraph reactivation workflow for a lead."""
    logger.info("workflow_task_start lead_id=%s campaign_id=%s org_id=%s", lead_id, campaign_id, org_id)

    # Celery workers are forked processes — configure_langfuse() is idempotent
    # and ensures env vars are populated in this process.
    configure_langfuse()

    # Abandon stale asyncpg connections before creating a new event loop.
    # close=False skips the async close, preventing "Future attached to a
    # different loop" when asyncio.run() starts a fresh loop each invocation.
    from app.db.base import dispose_engine_sync
    dispose_engine_sync()

    @observe(name="reactivation_workflow")
    async def _run():
        from langfuse import propagate_attributes  # type: ignore[import]
        from app.workflows.graph import get_compiled_graph
        from app.workflows.state import ReactivationState

        graph = get_compiled_graph()
        initial_state: ReactivationState = {
            "lead_id": lead_id,
            "campaign_id": campaign_id,
            "org_id": org_id,
            "error": None,
            "retry_count": 0,
        }
        thread_id = f"{campaign_id}:{lead_id}"
        config = {"configurable": {"thread_id": thread_id}}

        with propagate_attributes(
            user_id=lead_id,
            session_id=f"{campaign_id}:{lead_id}",
            metadata={"campaign_id": campaign_id, "org_id": org_id},
            tags=["workflow", "reactivation"],
        ):
            result = await graph.ainvoke(initial_state, config=config)
        return result

    try:
        result = asyncio.run(_run())
        flush_langfuse()
        logger.info("workflow_task_complete lead_id=%s result_keys=%s", lead_id, list(result.keys()))
        return {"status": "completed", "lead_id": lead_id}
    except Exception as exc:
        flush_langfuse()
        logger.error("workflow_task_failed lead_id=%s error=%s", lead_id, exc)
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.tasks.workflow_tasks.resume_workflow_after_approval",
    queue="workflows",
)
def resume_workflow_after_approval(thread_id: str, approval_status: str) -> dict:
    """Resume a suspended LangGraph workflow after human approval decision."""
    logger.info("workflow_resume thread_id=%s approval_status=%s", thread_id, approval_status)

    configure_langfuse()

    from app.db.base import dispose_engine_sync
    dispose_engine_sync()

    @observe(name="reactivation_workflow_resume")
    async def _resume():
        from langfuse import propagate_attributes  # type: ignore[import]
        from app.workflows.graph import get_compiled_graph

        graph = get_compiled_graph()
        config = {"configurable": {"thread_id": thread_id}}

        with propagate_attributes(
            metadata={"thread_id": thread_id, "approval_status": approval_status},
            tags=["workflow", "reactivation", "resume"],
        ):
            result = await graph.ainvoke(
                {"approval_status": approval_status},
                config=config,
            )
        return result

    try:
        result = asyncio.run(_resume())
        flush_langfuse()
        logger.info("workflow_resume_complete thread_id=%s", thread_id)
        return {"status": "resumed", "thread_id": thread_id}
    except Exception as exc:
        flush_langfuse()
        logger.error("workflow_resume_failed thread_id=%s error=%s", thread_id, exc)
        raise
