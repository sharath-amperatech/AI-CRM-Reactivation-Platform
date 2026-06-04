"""v2: parent-child chunking on crm_activities, tracing columns on messages

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-01

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── crm_activities: parent-child chunking support ─────────
    op.add_column(
        "crm_activities",
        sa.Column(
            "parent_chunk_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("crm_activities.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "crm_activities",
        sa.Column("chunk_index", sa.Integer, nullable=True),
    )
    op.create_index(
        "ix_crm_activity_parent_chunk",
        "crm_activities",
        ["parent_chunk_id"],
    )

    # ── messages: Langfuse tracing + prompt versioning ────────
    op.add_column(
        "messages",
        sa.Column(
            "prompt_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("prompt_versions.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "messages",
        sa.Column("langfuse_trace_id", sa.String(255), nullable=True),
    )
    op.add_column(
        "messages",
        sa.Column(
            "reranker_scores",
            postgresql.JSONB,
            nullable=True,
        ),
    )
    op.create_index(
        "ix_messages_prompt_version",
        "messages",
        ["prompt_version_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_messages_prompt_version", table_name="messages")
    op.drop_column("messages", "reranker_scores")
    op.drop_column("messages", "langfuse_trace_id")
    op.drop_column("messages", "prompt_version_id")

    op.drop_index("ix_crm_activity_parent_chunk", table_name="crm_activities")
    op.drop_column("crm_activities", "chunk_index")
    op.drop_column("crm_activities", "parent_chunk_id")
