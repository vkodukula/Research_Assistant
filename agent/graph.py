from __future__ import annotations

import itertools
from typing import Literal

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage  # used for conceptual alignment

from agent.state import AgentState, ToolCall, ToolResult, FinalAnswer
from agent.trace import timed_call
from agent import policies
from agent.synth import synthesize_answer

from tools import build_default_registry

REGISTRY = build_default_registry()

_counter = itertools.count(1)
def new_call_id(prefix: str = "call") -> str:
    return f"{prefix}_{next(_counter):04d}"


def planner_node(state: AgentState) -> AgentState:
    """
    Plans and proposes tool calls. Designed to mirror what an LLM planner would do,
    but implemented deterministically for offline operation.
    """
    state.iteration += 1

    q = state.user_question
    terms = policies.extract_terms(q)

    do_search = policies.should_search(q)
    do_define = policies.should_define(q)
    do_summary = policies.wants_summary(q)

    plan = [
        "Parse the question and identify key concepts.",
        "Decide whether evidence is needed and which tools to use.",
        "Call tools and collect evidence with provenance.",
        "Reflect: if evidence is insufficient, do a targeted follow-up search.",
        "Synthesize a final answer with citations and a tool usage log.",
    ]

    if do_define:
        plan.insert(2, "Look up definitions for relevant terms.")
    if do_search:
        plan.insert(3, "Search the offline knowledge base for evidence.")
    if do_summary:
        plan.insert(4, "Summarize long evidence snippets to keep the answer readable.")

    state.plan = plan

    calls: list[ToolCall] = []
    if do_define and terms:
        for t in terms[:2]:
            calls.append(ToolCall(id=new_call_id(), name="lookup_definition", args={"term": t}))

    if do_search:
        calls.append(ToolCall(id=new_call_id(), name="search_web", args={"query": q, "k": 3}))

    if do_summary:
        calls.append(ToolCall(id=new_call_id(), name="summarize", args={"text": f"User asked: {q}", "max_sentences": 2}))

    state.tool_calls = calls
    return state


def route_after_planner(state: AgentState) -> Literal["act", "final"]:
    return "act" if state.tool_calls else "final"


def act_node(state: AgentState) -> AgentState:
    """
    Executes tool calls via registry; appends ToolResults to state and tool_log.
    """
    results: list[ToolResult] = []

    for call in state.tool_calls:
        spec = REGISTRY.get(call.name)
        timed = timed_call(spec.fn, **call.args)

        tr = ToolResult(
            id=call.id,
            name=call.name,
            args=call.args,
            output=timed.output,
            started_at_ms=timed.started_at_ms,
            finished_at_ms=timed.finished_at_ms,
        )
        results.append(tr)

    state.tool_results.extend(results)
    state.tool_log.extend(results)

    # Clear pending calls
    state.tool_calls = []
    return state


def reflect_node(state: AgentState) -> AgentState:
    """
    Decide if we need more evidence. If the question expects explanation/comparison and
    we have no meaningful search results, do another targeted pass (bounded).
    """
    q = state.user_question

    search_results = [r for r in state.tool_results if r.name == "search_web"]
    have_search = bool(search_results)
    search_is_empty = have_search and all("No offline KB results" in r.output for r in search_results)

    # Evidence required for “why/how/compare” style questions
    needs_evidence = policies.should_search(q)

    # Determine if we should try again
    state.needs_more_evidence = bool(needs_evidence and (not have_search or search_is_empty))
    return state


def route_after_reflect(state: AgentState) -> Literal["more_evidence", "final"]:
    if state.needs_more_evidence and state.iteration < state.max_iterations:
        return "more_evidence"
    return "final"


def more_evidence_node(state: AgentState) -> AgentState:
    """
    Targeted follow-up tool call. This makes the agent look and behave like a real research loop.
    """
    targeted_query = state.user_question + " overview examples tradeoffs"
    state.tool_calls = [ToolCall(id=new_call_id(), name="search_web", args={"query": targeted_query, "k": 3})]
    return state


def final_node(state: AgentState) -> AgentState:
    """
    Deterministic synthesis with citations. (Designed so a real LLM synthesizer
    could be swapped in later without changing the graph.)
    """
    answer_text, citations, confidence, limitations = synthesize_answer(state.user_question, state.tool_results)
    state.final = FinalAnswer(
        answer=answer_text,
        citations=citations,
        confidence=confidence,
        limitations=limitations,
    )
    return state


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("planner", planner_node)
    g.add_node("act", act_node)
    g.add_node("reflect", reflect_node)
    g.add_node("more_evidence", more_evidence_node)
    g.add_node("final", final_node)

    g.set_entry_point("planner")

    g.add_conditional_edges("planner", route_after_planner, {"act": "act", "final": "final"})
    g.add_edge("act", "reflect")
    g.add_conditional_edges("reflect", route_after_reflect, {"more_evidence": "more_evidence", "final": "final"})
    g.add_edge("more_evidence", "act")
    g.add_edge("final", END)

    return g.compile()