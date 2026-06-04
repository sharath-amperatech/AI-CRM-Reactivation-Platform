from __future__ import annotations

from typing import TypedDict


class ReactivationState(TypedDict, total=False):
    # ── Inputs ────────────────────────────────────────────────
    lead_id: str
    campaign_id: str
    org_id: str

    # ── fetch_lead ────────────────────────────────────────────
    lead: dict
    activities: list[dict]

    # ── retrieve_context ──────────────────────────────────────
    retrieved_chunks: list[dict]
    crm_context_summary: str
    retrieval_metadata: dict   # candidate_count, hyde_used, reranker_scores, stage_latencies_ms

    # ── classify_lead ─────────────────────────────────────────
    segment: str
    confidence: float
    classification_reasoning: str
    classification_model: str  # exact Azure deployment name used

    # ── generate_message ──────────────────────────────────────
    message_id: str
    subject: str
    message_body: str
    ai_reasoning: str
    trace_id: str
    prompt_version_id: str | None   # UUID of the active PromptVersion row, or None
    langfuse_trace_id: str          # Langfuse span ID — deep-link from approval UI

    # ── campaign context (propagated from campaign row) ───────
    campaign_channel: str           # email | sms | whatsapp

    # ── human_approval (post-interrupt) ───────────────────────
    approval_id: str
    approval_status: str            # pending | approved | rejected | edited
    final_message_body: str

    # ── send_message ──────────────────────────────────────────
    sent_at: str | None
    send_error: str | None
    external_message_id: str | None

    # ── wait_for_reply ────────────────────────────────────────
    reply_id: str | None
    reply_body: str | None
    reply_received_at: str | None

    # ── analyze_response ──────────────────────────────────────
    reply_sentiment: str | None
    reply_intent: str | None        # interested | not_interested | booked | needs_info

    # ── book_meeting / escalate ───────────────────────────────
    booking_id: str | None
    escalation_reason: str | None

    # ── Control ───────────────────────────────────────────────
    error: str | None
    retry_count: int
