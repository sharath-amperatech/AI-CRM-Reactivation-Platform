from __future__ import annotations

from app.workflows.state import ReactivationState


def route_after_approval(state: ReactivationState) -> str:
    if state.get("error"):
        return "escalate"
    status = state.get("approval_status", "pending")
    if status in ("approved", "edited"):
        return "send_message"
    return "__end__"  # rejected


def route_after_send(state: ReactivationState) -> str:
    if state.get("send_error"):
        return "escalate"
    return "wait_for_reply"


def route_after_analysis(state: ReactivationState) -> str:
    intent = state.get("reply_intent")
    if intent == "booked":
        return "book_meeting"
    if intent in ("not_interested", "unsubscribe"):
        return "escalate"
    # needs_info, interested without booking — escalate for SDR follow-up
    return "escalate"


def route_after_fetch(state: ReactivationState) -> str:
    if state.get("error"):
        return "escalate"
    return "retrieve_context"


def route_after_wait(state: ReactivationState) -> str:
    if state.get("reply_body"):
        return "analyze_response"
    return "__end__"  # no reply yet — durable execution re-runs this later
