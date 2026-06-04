from __future__ import annotations

import uuid

from app.core.logging import get_logger
from app.db.base import get_session_factory
from app.observability import observe
from app.services.rag_service import RAGService
from app.workflows.state import ReactivationState

logger = get_logger(__name__)


@observe(name="retrieve_context")
async def retrieve_context(state: ReactivationState) -> ReactivationState:
    if state.get("error"):
        return state

    lead_id = uuid.UUID(state["lead_id"])
    org_id = uuid.UUID(state["org_id"])
    lead = state.get("lead", {})

    # Build query — include segment hint if already known from a prior run
    segment_hint = state.get("segment", lead.get("segment", ""))
    query = (
        f"Reactivation context for {lead.get('name', '')} "
        f"at {lead.get('company', '')}. "
        f"Segment: {segment_hint}. "
        f"Deal value: {lead.get('deal_value', '')}."
    )

    factory = get_session_factory()
    async with factory() as db:
        rag = RAGService(db)
        chunks, context_str, rag_meta = await rag.get_lead_context(
            lead_id,
            org_id,
            query,
            lead_info=lead,
        )

    chunks_serialized = [
        {
            "activity_id": str(c.activity_id),
            "content": c.content,
            "activity_type": c.activity_type,
            "occurred_at": c.occurred_at,
            "similarity_score": c.similarity_score,
            "rerank_score": c.rerank_score,
            "is_parent": c.is_parent,
        }
        for c in chunks
    ]

    retrieval_metadata = {
        "candidate_count": rag_meta.candidate_count,
        "hyde_used": rag_meta.hyde_used,
        "reranker_scores": rag_meta.reranker_scores,
        "stage_latencies_ms": rag_meta.stage_latencies_ms,
    }

    logger.info(
        "workflow_retrieve_context_done",
        lead_id=str(lead_id),
        chunk_count=len(chunks_serialized),
        hyde_used=rag_meta.hyde_used,
        latencies=rag_meta.stage_latencies_ms,
        query=query,
        context_preview=context_str[:300],
    )
    return {
        **state,
        "retrieved_chunks": chunks_serialized,
        "crm_context_summary": context_str,
        "retrieval_metadata": retrieval_metadata,
    }
