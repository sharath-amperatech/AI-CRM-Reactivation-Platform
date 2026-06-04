"""Initial schema — all tables, enums, extensions, indexes

Revision ID: 0001
Revises:
Create Date: 2026-05-26

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Extensions ────────────────────────────────────────────
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')

    # ── Enum types ────────────────────────────────────────────
    user_role = postgresql.ENUM(
        "admin", "sales_manager", "sdr", "read_only", name="user_role", create_type=False
    )
    lead_segment = postgresql.ENUM(
        "pricing_objection", "timing_issue", "competitor_loss", "ghosted",
        "no_decision_maker", "budget_constraints", "feature_gap", "unknown",
        name="lead_segment", create_type=False,
    )
    lead_status = postgresql.ENUM(
        "dormant", "active", "reactivated", "lost", "meeting_booked",
        name="lead_status", create_type=False,
    )
    activity_type = postgresql.ENUM(
        "email", "call", "meeting", "note", "deal_update",
        name="activity_type", create_type=False,
    )
    sentiment_type = postgresql.ENUM(
        "positive", "neutral", "negative", name="sentiment_type", create_type=False
    )
    campaign_status = postgresql.ENUM(
        "draft", "active", "paused", "completed", name="campaign_status", create_type=False
    )
    message_channel = postgresql.ENUM(
        "email", "sms", "whatsapp", name="message_channel", create_type=False
    )
    message_status = postgresql.ENUM(
        "draft", "pending_approval", "approved", "sent", "failed", "rejected",
        name="message_status", create_type=False,
    )
    approval_status = postgresql.ENUM(
        "pending", "approved", "rejected", "edited", name="approval_status", create_type=False
    )

    for enum in [
        user_role, lead_segment, lead_status, activity_type, sentiment_type,
        campaign_status, message_channel, message_status, approval_status,
    ]:
        enum.create(op.get_bind(), checkfirst=True)

    # ── 1. organizations ──────────────────────────────────────
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("plan", sa.String(50), nullable=False, server_default="starter"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("settings", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"])

    # ── 2. embedding_versions ─────────────────────────────────
    op.create_table(
        "embedding_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("dimension", sa.Integer, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ── 3. users ──────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("clerk_user_id", sa.String(255), nullable=True, unique=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role", postgresql.ENUM(name="user_role", create_type=False),
                  nullable=False, server_default="sdr"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("api_key_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_org_id", "users", ["org_id"])
    op.create_index("ix_users_clerk_user_id", "users", ["clerk_user_id"])
    op.create_index("ix_users_email", "users", ["email"])

    # ── 4. leads ──────────────────────────────────────────────
    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hubspot_id", sa.String(100), nullable=True, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("role", sa.String(255), nullable=True),
        sa.Column("segment", postgresql.ENUM(name="lead_segment", create_type=False),
                  nullable=False, server_default="unknown"),
        sa.Column("status", postgresql.ENUM(name="lead_status", create_type=False),
                  nullable=False, server_default="dormant"),
        sa.Column("confidence", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("deal_value", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("inactive_days", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("assigned_to_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("company_size", sa.String(50), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("tags", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_leads_org_status_segment", "leads", ["org_id", "status", "segment"])
    op.create_index("ix_leads_org_inactive_days", "leads", ["org_id", sa.text("inactive_days DESC")])
    op.create_index("ix_leads_assigned", "leads", ["assigned_to_id"])
    op.create_index("ix_leads_email", "leads", ["email"])
    op.execute("CREATE INDEX ix_leads_email_trgm ON leads USING gin(email gin_trgm_ops)")

    # ── 5. crm_activities ─────────────────────────────────────
    op.create_table(
        "crm_activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", postgresql.ENUM(name="activity_type", create_type=False), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("sentiment", postgresql.ENUM(name="sentiment_type", create_type=False), nullable=True),
        sa.Column("author", sa.String(255), nullable=True),
        sa.Column("hubspot_engagement_id", sa.String(100), nullable=True),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("embedding_version_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("embedding_versions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_crm_activity_lead_occurred", "crm_activities", ["lead_id", sa.text("occurred_at DESC")])
    op.create_index("ix_crm_activity_org", "crm_activities", ["org_id"])
    op.create_index("ix_crm_activity_hubspot_id", "crm_activities", ["hubspot_engagement_id"])
    # IVFFlat ANN index — created after initial data load for effectiveness
    op.execute(
        "CREATE INDEX ix_crm_activity_embedding_ivfflat "
        "ON crm_activities USING ivfflat (embedding vector_cosine_ops) "
        "WITH (lists = 100)"
    )

    # ── 6. campaigns ──────────────────────────────────────────
    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("status", postgresql.ENUM(name="campaign_status", create_type=False),
                  nullable=False, server_default="draft"),
        sa.Column("segment", sa.String(50), nullable=False, server_default="all"),
        sa.Column("channel", postgresql.ENUM(name="message_channel", create_type=False),
                  nullable=False, server_default="email"),
        sa.Column("ab_test", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("enrolled_leads", sa.Integer, nullable=False, server_default="0"),
        sa.Column("open_rate", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("reply_rate", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("meetings_booked", sa.Integer, nullable=False, server_default="0"),
        sa.Column("converted_leads", sa.Integer, nullable=False, server_default="0"),
        sa.Column("revenue_recovered", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("total_steps", sa.Integer, nullable=False, server_default="10"),
        sa.Column("steps_completed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("config", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_campaigns_org_id", "campaigns", ["org_id"])
    op.create_index("ix_campaigns_status", "campaigns", ["status"])

    # ── 7. campaign_enrollments ───────────────────────────────
    op.create_table(
        "campaign_enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="enrolled"),
        sa.Column("current_step", sa.Integer, nullable=False, server_default="0"),
        sa.Column("workflow_thread_id", sa.String(255), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint("uq_campaign_enrollment", "campaign_enrollments", ["campaign_id", "lead_id"])
    op.create_index("ix_enrollment_campaign", "campaign_enrollments", ["campaign_id"])
    op.create_index("ix_enrollment_lead", "campaign_enrollments", ["lead_id"])
    op.create_index("ix_enrollment_org", "campaign_enrollments", ["org_id"])

    # ── 8. messages ───────────────────────────────────────────
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("subject", sa.String(500), nullable=True),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("status", postgresql.ENUM(name="message_status", create_type=False),
                  nullable=False, server_default="draft"),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("external_message_id", sa.String(255), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_messages_lead_campaign", "messages", ["lead_id", "campaign_id"])
    op.create_index("ix_messages_status", "messages", ["status"])
    op.create_index("ix_messages_org", "messages", ["org_id"])

    # ── 9. approvals ──────────────────────────────────────────
    op.create_table(
        "approvals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", postgresql.ENUM(name="approval_status", create_type=False),
                  nullable=False, server_default="pending"),
        sa.Column("confidence", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("crm_context", sa.Text, nullable=True),
        sa.Column("ai_reasoning", sa.Text, nullable=True),
        sa.Column("retrieved_chunks", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("trace_id", sa.String(255), nullable=True),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("edited_body", sa.Text, nullable=True),
        sa.Column("rejection_reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_approvals_org_status", "approvals", ["org_id", "status"])
    op.create_index("ix_approvals_message", "approvals", ["message_id"])
    op.create_index("ix_approvals_trace_id", "approvals", ["trace_id"])

    # ── 10. replies ───────────────────────────────────────────
    op.create_table(
        "replies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("sentiment", sa.String(20), nullable=True),
        sa.Column("classification", sa.String(50), nullable=True),
        sa.Column("external_reply_id", sa.String(255), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_replies_message", "replies", ["message_id"])
    op.create_index("ix_replies_org", "replies", ["org_id"])

    # ── 11. bookings ──────────────────────────────────────────
    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("calendly_event_id", sa.String(255), nullable=True, unique=True),
        sa.Column("booked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("meeting_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="scheduled"),
        sa.Column("meeting_url", sa.String(500), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_bookings_lead", "bookings", ["lead_id"])
    op.create_index("ix_bookings_org", "bookings", ["org_id"])

    # ── 12. audit_logs ────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("changes", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_logs_org_created", "audit_logs", ["org_id", sa.text("created_at DESC")])
    op.create_index("ix_audit_logs_resource", "audit_logs", ["resource_type", "resource_id"])

    # ── 13. prompt_versions ───────────────────────────────────
    op.create_table(
        "prompt_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("template", sa.Text, nullable=False),
        sa.Column("variables", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint("uq_prompt_version", "prompt_versions", ["org_id", "name", "version"])
    op.create_index("ix_prompt_versions_active", "prompt_versions", ["org_id", "name", "is_active"])

    # ── 14. embedding_jobs ────────────────────────────────────
    op.create_table(
        "embedding_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("embedding_version_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("embedding_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("total_records", sa.Integer, nullable=False, server_default="0"),
        sa.Column("processed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("failed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_text", sa.Text, nullable=True),
        sa.Column("celery_task_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_embedding_jobs_status", "embedding_jobs", ["status"])
    op.create_index("ix_embedding_jobs_org", "embedding_jobs", ["org_id"])

    # ── 15. eval_runs ─────────────────────────────────────────
    op.create_table(
        "eval_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("triggered_by", sa.String(100), nullable=True),
        sa.Column("num_samples", sa.Integer, nullable=False, server_default="0"),
        sa.Column("faithfulness", sa.Float, nullable=True),
        sa.Column("answer_relevancy", sa.Float, nullable=True),
        sa.Column("context_recall", sa.Float, nullable=True),
        sa.Column("context_precision", sa.Float, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_text", sa.String(1000), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_eval_runs_org", "eval_runs", ["org_id"])
    op.create_index("ix_eval_runs_status", "eval_runs", ["status"])

    # ── 16. golden_dataset ────────────────────────────────────
    op.create_table(
        "golden_dataset",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("uuid_generate_v4()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("context", sa.Text, nullable=False),
        sa.Column("ground_truth", sa.Text, nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_golden_dataset_org", "golden_dataset", ["org_id"])
    op.create_index("ix_golden_dataset_category", "golden_dataset", ["category"])


def downgrade() -> None:
    op.drop_table("golden_dataset")
    op.drop_table("eval_runs")
    op.drop_table("embedding_jobs")
    op.drop_table("prompt_versions")
    op.drop_table("audit_logs")
    op.drop_table("bookings")
    op.drop_table("replies")
    op.drop_table("approvals")
    op.drop_table("messages")
    op.drop_table("campaign_enrollments")
    op.drop_table("campaigns")
    op.drop_table("crm_activities")
    op.drop_table("leads")
    op.drop_table("users")
    op.drop_table("embedding_versions")
    op.drop_table("organizations")

    for enum_name in [
        "approval_status", "message_status", "message_channel",
        "campaign_status", "sentiment_type", "activity_type",
        "lead_status", "lead_segment", "user_role",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")

    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
    op.execute("DROP EXTENSION IF EXISTS vector")
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
