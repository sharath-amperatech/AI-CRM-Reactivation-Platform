from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, get_current_user, get_org_id
from app.db.session import get_db
from app.models.user import User
from app.schemas.quality import EvalRunRead, EvalRunTrigger, RAGASMetricsResponse
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/quality", tags=["quality"])


@router.get("/metrics", response_model=RAGASMetricsResponse)
async def get_metrics(
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = EvaluationService(db)
    return await svc.get_latest_metrics(org_id=org_id)


@router.get("/evaluations", response_model=list[EvalRunRead])
async def get_eval_history(
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    svc = EvaluationService(db)
    runs = await svc.get_eval_history(org_id=org_id)
    return runs


@router.post("/run-evaluation", response_model=EvalRunRead, status_code=202)
async def trigger_evaluation(
    body: EvalRunTrigger,
    org_id: uuid.UUID = Depends(get_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.tasks.evaluation_tasks import run_ragas_evaluation
    run_ragas_evaluation.delay(org_id=str(org_id), num_samples=body.num_samples)

    # Return a stub — actual results appear when the task completes
    svc = EvaluationService(db)
    from app.models.eval_run import EvalRun
    placeholder = EvalRun(org_id=org_id, status="queued", triggered_by=str(user.id))
    db.add(placeholder)
    await db.flush()
    return placeholder
