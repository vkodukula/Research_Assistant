from __future__ import annotations

import re
from typing import Dict, List, Tuple

from tools.kb import KB


DEFINITIONS: Dict[str, str] = {
    "langchain": "A framework for building LLM apps using composable components like tools, chains, and agents.",
    "langgraph": "A graph-based orchestration framework for multi-step, stateful agent workflows.",
    "rag": "Retrieval-Augmented Generation: retrieve context first, then generate grounded answers with evidence.",
    "function calling": "A pattern where a model emits structured tool invocation requests (name + JSON args).",
    "citations": "References to evidence; here, citations point to tool call IDs that produced supporting outputs.",
}


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def lookup_definition(term: str) -> str:
    key = term.strip().lower()
    return DEFINITIONS.get(key, f"No definition found for '{term}'. Extend DEFINITIONS to add it.")


def summarize(text: str, max_sentences: int = 2) -> str:
    cleaned = " ".join(text.split())
    parts = re.split(r"\.\s+", cleaned)
    parts = [p.strip() for p in parts if p.strip()]
    out = ". ".join(parts[:max_sentences])
    if out and not out.endswith("."):
        out += "."
    return out


def search_web(query: str, k: int = 3) -> str:
    """
    Offline retrieval: token overlap scoring over a tiny KB.
    Output includes doc provenance via doc_id.
    """
    q_tokens = set(_tokenize(query))
    scored: List[Tuple[int, dict]] = []

    for doc in KB:
        d_tokens = set(_tokenize(doc["title"] + " " + doc["text"] + " " + " ".join(doc["tags"])))
        score = len(q_tokens & d_tokens)
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    hits = [doc for score, doc in scored if score > 0][:k]

    if not hits:
        return f"No offline KB results for query='{query}'. (KB is small; add more docs in tools/kb.py.)"

    lines = []
    for i, doc in enumerate(hits, 1):
        lines.append(f"{i}. {doc['title']} (doc_id={doc['id']}) — {doc['text']}")
    return "\n".join(lines)