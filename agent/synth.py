from __future__ import annotations

from typing import List, Tuple

from agent.state import Citation, ToolResult
from tools.implementations import summarize


def build_citations(results_used: List[ToolResult]) -> List[Citation]:
    return [Citation(tool=r.name, call_id=r.id) for r in results_used]


def format_citation_block(citations: List[Citation]) -> str:
    if not citations:
        return "[no sources used]"
    return " ".join([f"[source: {c.tool}#{c.call_id}]" for c in citations])


def synthesize_answer(question: str, tool_results: List[ToolResult]) -> Tuple[str, List[Citation], str, List[str]]:
    """
    Deterministic synthesis: use tool outputs, cite every tool output that contributes to content.
    Returns: (answer_text, citations, confidence, limitations)
    """
    q = question.lower()

    defs = [r for r in tool_results if r.name == "lookup_definition"]
    searches = [r for r in tool_results if r.name == "search_web"]
    sums = [r for r in tool_results if r.name == "summarize"]

    used: List[ToolResult] = []
    parts: List[str] = []

    if defs:
        parts.append("## Definitions")
        for r in defs:
            term = r.args.get("term", "term")
            parts.append(f"- **{term}**: {r.output} [source: {r.name}#{r.id}]")
            used.append(r)

    if searches:
        parts.append("\n## Evidence (offline search)")
        for r in searches:
            # Keep evidence readable but still grounded
            brief = summarize(r.output, max_sentences=2)
            parts.append(f"- {brief} [source: {r.name}#{r.id}]")
            used.append(r)

    if sums:
        parts.append("\n## Additional Summary")
        for r in sums:
            parts.append(f"- {r.output} [source: {r.name}#{r.id}]")
            used.append(r)

    parts.append("\n## Answer")
    if "langgraph" in q:
        parts.append(
            "LangGraph is most useful when you want **explicit, stateful control** over multi-step workflows: "
            "branching, loops (tool-use cycles), and clear execution structure. For a research assistant, that maps "
            "cleanly onto a graph: **plan → tool calls → reflect → retry → synthesize**, with state and audit logs."
        )
    elif "rag" in q:
        parts.append(
            "RAG (Retrieval-Augmented Generation) improves reliability by grounding generation in retrieved context. "
            "Even in this offline version, the same principle applies: retrieve evidence first, then generate, and cite "
            "the evidence-producing tool calls."
        )
    elif "compare" in q or "difference" in q:
        parts.append(
            "This assistant answers comparison questions by first retrieving evidence (offline KB search), then synthesizing "
            "trade-offs into a readable summary. When evidence is insufficient, it performs a targeted follow-up search pass."
        )
    else:
        parts.append(
            "This assistant decides when to retrieve evidence from tools, gathers it, and produces a citation-backed answer. "
            "The tool usage log makes the workflow auditable and easy to debug."
        )

    limitations = [
        "No real web access: `search_web` queries a small offline KB.",
        "Planning/reflection are deterministic heuristics (no hosted LLM).",
        "Coverage depends on KB content; extend `tools/kb.py` for broader knowledge.",
    ]

    # Confidence heuristic
    confidence = "medium"
    if searches:
        if any("No offline KB results" in r.output for r in searches):
            confidence = "low"
        else:
            confidence = "high"

    citations = build_citations(used)
    answer_text = "\n".join(parts) + "\n\nCitations: " + format_citation_block(citations)

    return answer_text, citations, confidence, limitations