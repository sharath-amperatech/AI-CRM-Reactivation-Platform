"""Semantic cache backed by Redis.

Caches LLM-generated message bodies keyed by the embedding of the query.
Before calling the LLM, check if a semantically similar query was already
answered (cosine similarity >= threshold). Cache TTL: 1 hour.

Usage:
    cache = SemanticCache()
    hit = await cache.get(embedding)
    if hit:
        return hit
    result = await llm_call(...)
    await cache.set(embedding, result)
"""
from __future__ import annotations

import json
import math
import time
import uuid
from typing import Any

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_CACHE_TTL_SECONDS = 3600  # 1 hour
_SIMILARITY_THRESHOLD = 0.97
_KEY_PREFIX = "riq:semcache:"
_INDEX_KEY = "riq:semcache:index"


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class SemanticCache:
    """Redis-backed semantic cache using embedding cosine similarity."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            import redis.asyncio as aioredis  # type: ignore[import]
            self._client = aioredis.from_url(
                self._settings.REDIS_URL, decode_responses=True
            )
        return self._client

    async def get(self, query_embedding: list[float]) -> str | None:
        """Return cached response if a semantically similar query exists, else None."""
        try:
            client = self._get_client()
            # Fetch all entry IDs from the index
            entry_ids: list[str] = await client.lrange(_INDEX_KEY, 0, -1)
            if not entry_ids:
                return None

            best_score = 0.0
            best_value: str | None = None

            for entry_id in entry_ids:
                raw = await client.get(f"{_KEY_PREFIX}{entry_id}")
                if raw is None:
                    continue
                entry = json.loads(raw)
                sim = _cosine_similarity(query_embedding, entry["embedding"])
                if sim > best_score:
                    best_score = sim
                    best_value = entry["value"]

            if best_score >= _SIMILARITY_THRESHOLD and best_value is not None:
                logger.info("semantic_cache_hit", similarity=round(best_score, 4))
                return best_value

            return None
        except Exception as exc:
            logger.warning("semantic_cache_get_error", error=str(exc))
            return None

    async def set(self, query_embedding: list[float], value: str) -> None:
        """Store a new entry in the cache with TTL."""
        try:
            client = self._get_client()
            entry_id = str(uuid.uuid4())
            entry = {
                "embedding": query_embedding,
                "value": value,
                "ts": time.time(),
            }
            key = f"{_KEY_PREFIX}{entry_id}"
            await client.set(key, json.dumps(entry), ex=_CACHE_TTL_SECONDS)
            await client.lpush(_INDEX_KEY, entry_id)
            # Trim the index to keep memory bounded (max 1000 recent entries)
            await client.ltrim(_INDEX_KEY, 0, 999)
            logger.info("semantic_cache_set", entry_id=entry_id)
        except Exception as exc:
            logger.warning("semantic_cache_set_error", error=str(exc))
