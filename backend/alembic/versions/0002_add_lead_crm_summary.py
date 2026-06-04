"""Add crm_summary column to leads table

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-30

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("crm_summary", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("leads", "crm_summary")
