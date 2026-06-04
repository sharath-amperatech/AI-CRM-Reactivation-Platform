from __future__ import annotations

import uuid

from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.mixins import Base, TimestampMixin


class EmbeddingVersion(TimestampMixin, Base):
    __tablename__ = "embedding_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    embedding_jobs: Mapped[list["EmbeddingJob"]] = relationship(  # noqa: F821
        "EmbeddingJob", back_populates="embedding_version"
    )

    def __repr__(self) -> str:
        return f"<EmbeddingVersion {self.name} dim={self.dimension}>"
