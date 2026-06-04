"""Reranking module: Cohere Rerank API with BGE-Reranker local fallback.

Usage:
    from app.reranker import rerank

    reranked = await rerank(query, chunks, top_n=5)

Returns the same list type passed in, sorted by relevance score descending,
truncated to top_n. Each item gains a .rerank_score attribute.
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@runtime_checkable
class Rankable(Protocol):
    content: str
    rerank_score: float | None


async def _cohere_rerank(
    query: str,
    chunks: list[Any],
    top_n: int,
    api_key: str,
) -> list[Any]:
    import cohere  # type: ignore[import]

    client = cohere.AsyncClient(api_key=api_key)
    documents = [c.content for c in chunks]
    response = await client.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=documents,
        top_n=top_n,
    )
    reranked: list[Any] = []
    for result in response.results:
        chunk = chunks[result.index]
        chunk.rerank_score = result.relevance_score
        reranked.append(chunk)
    logger.info("cohere_rerank_done", input=len(chunks), output=len(reranked))
    return reranked


async def _bge_rerank(
    query: str,
    chunks: list[Any],
    top_n: int,
) -> list[Any]:
    """Local BGE-Reranker fallback using sentence-transformers cross-encoder."""
    try:
        from sentence_transformers import CrossEncoder  # type: ignore[import]
        import asyncio

        model = CrossEncoder("BAAI/bge-reranker-v2-m3")
        pairs = [(query, c.content) for c in chunks]
        scores = await asyncio.get_event_loop().run_in_executor(
            None, model.predict, pairs
        )
        for chunk, score in zip(chunks, scores):
            chunk.rerank_score = float(score)
        ranked = sorted(chunks, key=lambda c: c.rerank_score or 0.0, reverse=True)
        logger.info("bge_rerank_done", input=len(chunks), output=len(ranked[:top_n]))
        return ranked[:top_n]
    except ImportError:
        logger.warning("bge_reranker_not_available, falling back to similarity order")
        for c in chunks:
            if c.rerank_score is None:
                c.rerank_score = getattr(c, "similarity_score", 0.0)
        return chunks[:top_n]


async def rerank(
    query: str,
    chunks: list[Any],
    top_n: int | None = None,
) -> list[Any]:
    """Rerank chunks by relevance to query. Cohere if key configured, else BGE."""
    if not chunks:
        return chunks

    settings = get_settings()
    top_n = top_n or settings.RERANK_TOP_N
    cohere_key = settings.COHERE_API_KEY.get_secret_value() if settings.COHERE_API_KEY else ""

    if cohere_key:
        try:
            return await _cohere_rerank(query, chunks, top_n, cohere_key)
        except Exception as exc:
            logger.warning("cohere_rerank_failed_falling_back", error=str(exc))

    return await _bge_rerank(query, chunks, top_n)
