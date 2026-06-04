"""RAG service — v2 three-stage pipeline.

Stage 1  : PGVector cosine similarity (top-50 child chunks, active embedding version)
Stage 1b : HyDE — if fewer than 5 chunks retrieved, generate a hypothetical CRM note
           and re-embed it as the query, then repeat Stage 1.
Stage 2  : Reranking via Cohere (or BGE local fallback), returns top-5.
Stage 3  : Parent expansion — swap each child chunk for its 1024-token parent chunk.

The pipeline returns (chunks, context_str, metadata) where metadata carries
latency-per-stage and reranker scores for Langfuse tracing.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.azure_openai import azure_client
from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.crm_activity import CRMActivity
from app.reranker import rerank
from app.services.embedding_service import EmbeddingService

logger = get_logger(__name__)

# Leads with fewer retrieved chunks than this trigger HyDE
_HYDE_THRESHOLD = 5
# Top-K candidates to retrieve before reranking
_CANDIDATE_K = 50


@dataclass
class RetrievedChunk:
    activity_id: uuid.UUID
    lead_id: uuid.UUID
    content: str
    activity_type: str
    occurred_at: str
    similarity_score: float
    rerank_score: float | None = None
    is_parent: bool = False


@dataclass
class RAGMetadata:
    candidate_count: int = 0
    hyde_used: bool = False
    reranker_scores: list[dict] = field(default_factory=list)
    stage_latencies_ms: dict[str, float] = field(default_factory=dict)


_HYDE_PROMPT = (
    "You are a CRM assistant. Write a realistic one-paragraph CRM note for a sales rep "
    "who is trying to reactivate a dormant lead. The lead's profile:\n\n"
    "Name: {name}\nCompany: {company}\nSegment: {segment}\nDeal value: ${deal_value}\n\n"
    "The note should describe the most likely reason this lead went silent and what "
    "relevant context a rep would want when reaching out again. Be specific, not generic."
)


class RAGService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._settings = get_settings()
        self._embedding_svc = EmbeddingService(db)

    # ──────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────

    async def get_lead_context(
        self,
        lead_id: uuid.UUID,
        org_id: uuid.UUID,
        query: str,
        lead_info: dict | None = None,
    ) -> tuple[list[RetrievedChunk], str, RAGMetadata]:
        """Full 3-stage RAG pipeline. Returns (chunks, context_str, metadata)."""
        meta = RAGMetadata()

        # Stage 1 — candidate retrieval
        t0 = time.perf_counter()
        embedding = await self._embedding_svc.embed_text(query)
        candidates = await self._retrieve_child_chunks(lead_id, org_id, embedding)
        meta.candidate_count = len(candidates)
        meta.stage_latencies_ms["stage1_ms"] = round((time.perf_counter() - t0) * 1000, 1)

        # Stage 1b — HyDE for sparse histories
        if len(candidates) < _HYDE_THRESHOLD and lead_info:
            t1b = time.perf_counter()
            hyde_query = await self._generate_hyde_query(lead_info)
            if hyde_query:
                hyde_embedding = await self._embedding_svc.embed_text(hyde_query)
                hyde_candidates = await self._retrieve_child_chunks(
                    lead_id, org_id, hyde_embedding
                )
                if len(hyde_candidates) > len(candidates):
                    candidates = hyde_candidates
                    embedding = hyde_embedding
                    meta.hyde_used = True
                    logger.info(
                        "rag_hyde_applied",
                        lead_id=str(lead_id),
                        original_count=meta.candidate_count,
                        hyde_count=len(candidates),
                    )
            meta.stage_latencies_ms["stage1b_hyde_ms"] = round(
                (time.perf_counter() - t1b) * 1000, 1
            )

        # Stage 2 — reranking
        t2 = time.perf_counter()
        top_chunks = await rerank(query, candidates, top_n=self._settings.RERANK_TOP_N)
        logger.info(
            "rag_stage2_rerank",
            candidates_in=len(candidates),
            top_chunks_out=len(top_chunks),
            top_n=self._settings.RERANK_TOP_N,
        )
        meta.reranker_scores = [
            {
                "activity_id": str(c.activity_id),
                "rerank_score": c.rerank_score,
                "similarity_score": c.similarity_score,
            }
            for c in top_chunks
        ]
        meta.stage_latencies_ms["stage2_rerank_ms"] = round(
            (time.perf_counter() - t2) * 1000, 1
        )

        # Stage 3 — parent expansion
        t3 = time.perf_counter()
        final_chunks = await self._expand_to_parents(top_chunks)
        logger.info(
            "rag_stage3_expand",
            top_chunks_in=len(top_chunks),
            final_chunks_out=len(final_chunks),
        )
        meta.stage_latencies_ms["stage3_parent_expand_ms"] = round(
            (time.perf_counter() - t3) * 1000, 1
        )

        context_str = self._format_context(final_chunks)

        logger.info(
            "rag_pipeline_done",
            lead_id=str(lead_id),
            candidates=meta.candidate_count,
            top_k=len(top_chunks),
            hyde=meta.hyde_used,
            latencies=meta.stage_latencies_ms,
        )
        return final_chunks, context_str, meta

    # ──────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────

    async def _retrieve_child_chunks(
        self,
        lead_id: uuid.UUID,
        org_id: uuid.UUID,
        embedding: list[float],
    ) -> list[RetrievedChunk]:
        """Cosine similarity search restricted to child chunks (or flat chunks)
        for this lead, filtered by the active embedding version."""
        active_version = await self._embedding_svc.get_active_embedding_version()

        rows = await self._run_similarity_query(
            lead_id, org_id, embedding, active_version_id=active_version.id if active_version else None
        )

        # If the version filter produced no results, retry without it so that
        # activities embedded before versioning was introduced are still found.
        if not rows and active_version:
            logger.info(
                "rag_version_filter_miss",
                lead_id=str(lead_id),
                version_id=str(active_version.id),
            )
            rows = await self._run_similarity_query(
                lead_id, org_id, embedding, active_version_id=None
            )

        logger.info(
            "rag_candidate_rows",
            lead_id=str(lead_id),
            count=len(rows),
            version_filter_applied=active_version is not None,
            threshold=self._settings.SIMILARITY_THRESHOLD,
        )

        return [
            RetrievedChunk(
                activity_id=row[0],
                lead_id=row[1],
                activity_type=str(row[2]),
                occurred_at=str(row[3]),
                content=row[4],
                similarity_score=float(row[5]),
            )
            for row in rows
        ]

    async def _run_similarity_query(
        self,
        lead_id: uuid.UUID,
        org_id: uuid.UUID,
        embedding: list[float],
        active_version_id: uuid.UUID | None,
    ) -> list:
        version_filter = "AND embedding_version_id = :version_id" if active_version_id else ""
        sql = text(f"""
            SELECT
                id, lead_id, type, occurred_at,
                COALESCE(summary, '') || ' ' || COALESCE(content, '') AS full_text,
                1 - (embedding <=> CAST(:query_embedding AS vector)) AS similarity,
                parent_chunk_id
            FROM crm_activities
            WHERE lead_id = :lead_id
              AND org_id = :org_id
              AND embedding IS NOT NULL
              AND 1 - (embedding <=> CAST(:query_embedding AS vector)) >= :threshold
              {version_filter}
            ORDER BY embedding <=> CAST(:query_embedding AS vector)
            LIMIT :top_k
        """)
        params: dict = {
            "query_embedding": str(embedding),
            "lead_id": str(lead_id),
            "org_id": str(org_id),
            "threshold": self._settings.SIMILARITY_THRESHOLD,
            "top_k": _CANDIDATE_K,
        }
        if active_version_id:
            params["version_id"] = str(active_version_id)
        result = await self._db.execute(sql, params)
        return result.fetchall()

    async def _generate_hyde_query(self, lead_info: dict) -> str | None:
        """Generate a hypothetical CRM note via GPT-4.1-mini for sparse leads."""
        try:
            prompt = _HYDE_PROMPT.format(
                name=lead_info.get("name", "Unknown"),
                company=lead_info.get("company", "Unknown"),
                segment=lead_info.get("segment", "unknown"),
                deal_value=lead_info.get("deal_value", 0),
            )
            settings = get_settings()
            response = await azure_client.chat.completions.create(
                model=settings.AZURE_DEPLOYMENT_GPT41_MINI,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            logger.warning("hyde_generation_failed", error=str(exc))
            return None

    async def _expand_to_parents(
        self, chunks: list[RetrievedChunk]
    ) -> list[RetrievedChunk]:
        """For each chunk that has a parent_chunk_id, fetch and return the parent
        (1024-token context). Chunks without a parent are returned as-is."""
        # Collect all activity IDs we need to check for parent_chunk_id
        activity_ids = [c.activity_id for c in chunks]
        if not activity_ids:
            return chunks

        result = await self._db.execute(
            select(CRMActivity.id, CRMActivity.parent_chunk_id).where(
                CRMActivity.id.in_(activity_ids)
            )
        )
        id_to_parent = {row[0]: row[1] for row in result.fetchall()}

        parent_ids = [
            pid for pid in id_to_parent.values() if pid is not None
        ]

        parent_map: dict[uuid.UUID, CRMActivity] = {}
        if parent_ids:
            parent_result = await self._db.execute(
                select(CRMActivity).where(CRMActivity.id.in_(parent_ids))
            )
            for parent in parent_result.scalars().all():
                parent_map[parent.id] = parent

        expanded: list[RetrievedChunk] = []
        seen_parent_ids: set[uuid.UUID] = set()

        for chunk in chunks:
            parent_id = id_to_parent.get(chunk.activity_id)
            if parent_id and parent_id in parent_map:
                if parent_id in seen_parent_ids:
                    continue  # deduplicate: same parent referenced by multiple children
                seen_parent_ids.add(parent_id)
                parent = parent_map[parent_id]
                parent_content = " ".join(
                    filter(None, [parent.summary, parent.content])
                )
                expanded.append(
                    RetrievedChunk(
                        activity_id=parent.id,
                        lead_id=chunk.lead_id,
                        activity_type=str(parent.type),
                        occurred_at=str(parent.occurred_at),
                        content=parent_content,
                        similarity_score=chunk.similarity_score,
                        rerank_score=chunk.rerank_score,
                        is_parent=True,
                    )
                )
            else:
                expanded.append(chunk)

        return expanded

    @staticmethod
    def _format_context(chunks: list[RetrievedChunk]) -> str:
        if not chunks:
            return "No relevant context found."
        parts = []
        for i, chunk in enumerate(chunks, 1):
            label = "parent" if chunk.is_parent else "chunk"
            parts.append(
                f"[{i}] ({chunk.activity_type} — {chunk.occurred_at}) [{label}]\n{chunk.content}"
            )
        return "\n\n".join(parts)
