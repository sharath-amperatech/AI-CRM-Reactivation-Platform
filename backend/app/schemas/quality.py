from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import Field

from app.schemas.common import APIModel


class RAGASMetricPoint(APIModel):
    date: str
    faithfulness: float
    answer_relevancy: float
    context_recall: float
    context_precision: float


class RAGASMetricsResponse(APIModel):
    latest: RAGASMetricPoint | None
    history: list[RAGASMetricPoint]
    average_faithfulness: float | None = None
    average_answer_relevancy: float | None = None
    average_context_recall: float | None = None
    average_context_precision: float | None = None


class EvalRunRead(APIModel):
    id: uuid.UUID
    org_id: uuid.UUID
    status: str
    triggered_by: str | None
    num_samples: int
    faithfulness: float | None
    answer_relevancy: float | None
    context_recall: float | None
    context_precision: float | None
    started_at: datetime | None
    completed_at: datetime | None
    error_text: str | None
    created_at: datetime


class EvalRunTrigger(APIModel):
    num_samples: int = Field(default=50, ge=10, le=500)
