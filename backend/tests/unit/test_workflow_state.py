from __future__ import annotations

import pytest

from app.workflows.state import ReactivationState


def test_state_is_total_false():
    """ReactivationState should allow partial construction."""
    state: ReactivationState = {
        "lead_id": "test-lead-id",
        "campaign_id": "test-campaign-id",
        "org_id": "test-org-id",
        "error": None,
        "retry_count": 0,
    }
    assert state["lead_id"] == "test-lead-id"
    assert state.get("segment") is None


def test_state_accumulates_correctly():
    state: ReactivationState = {
        "lead_id": "l1",
        "campaign_id": "c1",
        "org_id": "o1",
        "error": None,
        "retry_count": 0,
    }
    updated = {**state, "segment": "pricing_objection", "confidence": 0.91}
    assert updated["segment"] == "pricing_objection"
    assert updated["lead_id"] == "l1"
