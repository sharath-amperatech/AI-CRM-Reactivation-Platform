from __future__ import annotations

import uuid
from typing import Any

from openai import AsyncAzureOpenAI
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.crm_activity import CRMActivity
from app.models.embedding_version import EmbeddingVersion

logger = get_logger(__name__)


class EmbeddingService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._settings = get_settings()
        self._client = AsyncAzureOpenAI(
            api_key=self._settings.AZURE_OPENAI_TEXT_EMBEDDING_API_KEY.get_secret_value(),
            azure_endpoint=self._settings.AZURE_OPENAI_TEXT_EMBEDDING_ENDPOINT,
            api_version=self._settings.AZURE_OPENAI_API_VERSION,
        )

    async def embed_text(self, text: str) -> list[float]:
        if not text.strip():
            return [0.0] * self._settings.EMBEDDING_DIMENSION

        response = await self._client.embeddings.create(
            input=text,
            model=self._settings.AZURE_OPENAI_TEXT_EMBEDDING_DEPLOYMENT,
        )
        return response.data[0].embedding

    async def embed_texts_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = await self._client.embeddings.create(
            input=texts,
            model=self._settings.AZURE_OPENAI_TEXT_EMBEDDING_DEPLOYMENT,
        )
        return [item.embedding for item in response.data]

    async def get_active_embedding_version(self) -> EmbeddingVersion | None:
        result = await self._db.execute(
            select(EmbeddingVersion).where(EmbeddingVersion.is_active == True)
        )
        return result.scalar_one_or_none()

    async def embed_activity(self, activity: CRMActivity) -> list[float] | None:
        text = " ".join(filter(None, [activity.summary, activity.content]))
        if not text:
            return None
        embedding = await self.embed_text(text)
        return embedding

    async def embed_activities_batch(
        self, activity_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, list[float]]:
        result = await self._db.execute(
            select(CRMActivity).where(CRMActivity.id.in_(activity_ids))
        )
        activities = result.scalars().all()
        version = await self.get_active_embedding_version()

        texts = [" ".join(filter(None, [a.summary, a.content])) for a in activities]
        embeddings = await self.embed_texts_batch(texts)

        results: dict[uuid.UUID, list[float]] = {}
        for activity, embedding in zip(activities, embeddings):
            activity.embedding = embedding
            if version:
                activity.embedding_version_id = version.id
            results[activity.id] = embedding

        await self._db.flush()
        logger.info("activities_embedded", count=len(results))
        return results
