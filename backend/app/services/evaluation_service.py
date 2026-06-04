from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.eval_run import EvalRun
from app.models.golden_dataset import GoldenDataset
from app.schemas.quality import EvalRunRead, RAGASMetricPoint, RAGASMetricsResponse

logger = get_logger(__name__)


class EvaluationService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._settings = get_settings()

    async def run_evaluation(
        self,
        org_id: uuid.UUID,
        num_samples: int = 50,
        triggered_by: str = "manual",
    ) -> EvalRun:
        run = EvalRun(
            org_id=org_id,
            status="running",
            triggered_by=triggered_by,
            num_samples=num_samples,
            started_at=datetime.now(timezone.utc),
        )
        self._db.add(run)
        await self._db.flush()

        try:
            samples = await self._load_samples(org_id, num_samples)
            if not samples:
                run.status = "completed"
                run.num_samples = 0
                run.completed_at = datetime.now(timezone.utc)
                await self._db.flush()
                return run

            scores = await self._compute_ragas_scores(samples)
            run.faithfulness = scores.get("faithfulness")
            run.answer_relevancy = scores.get("answer_relevancy")
            run.context_recall = scores.get("context_recall")
            run.context_precision = scores.get("context_precision")
            run.status = "completed"
            run.num_samples = len(samples)
            run.completed_at = datetime.now(timezone.utc)

            logger.info(
                "eval_run_complete",
                run_id=str(run.id),
                faithfulness=run.faithfulness,
                answer_relevancy=run.answer_relevancy,
            )
        except Exception as exc:
            run.status = "failed"
            run.error_text = str(exc)
            run.completed_at = datetime.now(timezone.utc)
            logger.error("eval_run_failed", run_id=str(run.id), error=str(exc))

        await self._db.flush()
        return run

    async def _load_samples(
        self, org_id: uuid.UUID, limit: int
    ) -> list[GoldenDataset]:
        result = await self._db.execute(
            select(GoldenDataset)
            .where(GoldenDataset.org_id == org_id)
            .order_by(GoldenDataset.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def _compute_ragas_scores(
        self, samples: list[GoldenDataset]
    ) -> dict[str, float]:
        # RAGAS evaluation scaffolding — full implementation plugs in here
        # Uses ragas library with configured LLM + embeddings
        logger.info("ragas_evaluation_placeholder", sample_count=len(samples))
        return {
            "faithfulness": 0.0,
            "answer_relevancy": 0.0,
            "context_recall": 0.0,
            "context_precision": 0.0,
        }

    async def get_latest_metrics(self, org_id: uuid.UUID) -> RAGASMetricsResponse:
        result = await self._db.execute(
            select(EvalRun)
            .where(EvalRun.org_id == org_id, EvalRun.status == "completed")
            .order_by(EvalRun.completed_at.desc())
            .limit(30)
        )
        runs = result.scalars().all()

        if not runs:
            return RAGASMetricsResponse(latest=None, history=[])

        history = [
            RAGASMetricPoint(
                date=str(r.completed_at.date()) if r.completed_at else "",
                faithfulness=r.faithfulness or 0.0,
                answer_relevancy=r.answer_relevancy or 0.0,
                context_recall=r.context_recall or 0.0,
                context_precision=r.context_precision or 0.0,
            )
            for r in runs
            if r.completed_at
        ]

        latest = history[0] if history else None
        return RAGASMetricsResponse(latest=latest, history=history)

    async def get_eval_history(
        self, org_id: uuid.UUID, limit: int = 20
    ) -> list[EvalRun]:
        result = await self._db.execute(
            select(EvalRun)
            .where(EvalRun.org_id == org_id)
            .order_by(EvalRun.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
