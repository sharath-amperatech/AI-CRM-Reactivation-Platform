from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.workflows.edges import (
    route_after_analysis,
    route_after_approval,
    route_after_fetch,
    route_after_send,
    route_after_wait,
)
from app.workflows.nodes.analyze_response import analyze_response
from app.workflows.nodes.book_meeting import book_meeting
from app.workflows.nodes.classify_lead import classify_lead
from app.workflows.nodes.escalate import escalate
from app.workflows.nodes.fetch_lead import fetch_lead
from app.workflows.nodes.generate_message import generate_message
from app.workflows.nodes.human_approval import human_approval
from app.workflows.nodes.retrieve_context import retrieve_context
from app.workflows.nodes.send_message import send_message
from app.workflows.nodes.wait_for_reply import wait_for_reply
from app.workflows.state import ReactivationState


def build_reactivation_graph():
    graph = StateGraph(ReactivationState)

    # ── Nodes ─────────────────────────────────────────────────
    graph.add_node("fetch_lead", fetch_lead)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("classify_lead", classify_lead)
    graph.add_node("generate_message", generate_message)
    graph.add_node("human_approval", human_approval)
    graph.add_node("send_message", send_message)
    graph.add_node("wait_for_reply", wait_for_reply)
    graph.add_node("analyze_response", analyze_response)
    graph.add_node("book_meeting", book_meeting)
    graph.add_node("escalate", escalate)

    # ── Edges ─────────────────────────────────────────────────
    graph.add_edge(START, "fetch_lead")
    graph.add_conditional_edges("fetch_lead", route_after_fetch, {
        "retrieve_context": "retrieve_context",
        "escalate": "escalate",
    })
    graph.add_edge("retrieve_context", "classify_lead")
    graph.add_edge("classify_lead", "generate_message")
    graph.add_edge("generate_message", "human_approval")
    graph.add_conditional_edges("human_approval", route_after_approval, {
        "send_message": "send_message",
        "__end__": END,
        "escalate": "escalate",
    })
    graph.add_conditional_edges("send_message", route_after_send, {
        "wait_for_reply": "wait_for_reply",
        "escalate": "escalate",
    })
    graph.add_conditional_edges("wait_for_reply", route_after_wait, {
        "analyze_response": "analyze_response",
        "__end__": END,
    })
    graph.add_conditional_edges("analyze_response", route_after_analysis, {
        "book_meeting": "book_meeting",
        "escalate": "escalate",
    })
    graph.add_edge("book_meeting", END)
    graph.add_edge("escalate", END)

    return graph.compile()


# Module-level singleton — lazy-initialized in main.py lifespan
_compiled_graph = None


def get_compiled_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_reactivation_graph()
    return _compiled_graph
