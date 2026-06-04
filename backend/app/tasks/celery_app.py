from __future__ import annotations

import sys

from celery import Celery
from celery.utils.log import get_task_logger

from app.core.config import get_settings

settings = get_settings()
logger = get_task_logger(__name__)


def create_celery_app() -> Celery:
    app = Celery("reactiviq")

    app.conf.update(
        broker_url=settings.CELERY_BROKER_URL,
        result_backend=settings.CELERY_RESULT_BACKEND,
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_routes={
            "app.tasks.workflow_tasks.*": {"queue": "workflows"},
            "app.tasks.embedding_tasks.*": {"queue": "embeddings"},
            "app.tasks.notification_tasks.*": {"queue": "notifications"},
            "app.tasks.hubspot_tasks.*": {"queue": "default"},
            "app.tasks.evaluation_tasks.*": {"queue": "default"},
        },
        beat_schedule={
            "hubspot-sync-every-hour": {
                "task": "app.tasks.hubspot_tasks.sync_all_orgs",
                "schedule": 3600.0,
            },
            "nightly-ragas-evaluation": {
                "task": "app.tasks.evaluation_tasks.run_nightly_evaluation",
                "schedule": 86400.0,
            },
        },
        imports=[
            "app.tasks.workflow_tasks",
            "app.tasks.embedding_tasks",
            "app.tasks.hubspot_tasks",
            "app.tasks.evaluation_tasks",
            "app.tasks.notification_tasks",
        ],
    )

    # prefork pool uses Unix semaphores unavailable on Windows
    if sys.platform == "win32":
        app.conf.worker_pool = "solo"

    return app


celery_app = create_celery_app()
