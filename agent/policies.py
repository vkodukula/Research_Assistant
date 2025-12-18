from __future__ import annotations

import re
from typing import List

# Terms the agent can proactively recognize for definitions.
KNOWN_TERMS = [
    "langgraph",
    "langchain",
    "rag",
    "function calling",
    "citations",
    "tool calling",
    "agent",
]


def extract_terms(question: str) -> List[str]:
    q = question.lower()
    found = []
    for t in KNOWN_TERMS:
        if t in q:
            found.append(t)
    # Also capture quoted terms: "..."
    found += re.findall(r'"([^"]+)"', question)
    # Deduplicate preserving order
    seen = set()
    out = []
    for x in found:
        x = x.strip().lower()
        if x and x not in seen:
            out.append(x)
            seen.add(x)
    return out


def should_search(question: str) -> bool:
    q = question.lower()
    triggers = [
        "what is",
        "explain",
        "why",
        "how",
        "compare",
        "difference",
        "pros",
        "cons",
        "evidence",
        "sources",
        "research",
        "best",
    ]
    return any(t in q for t in triggers)


def should_define(question: str) -> bool:
    q = question.lower()
    triggers = ["define", "definition", "meaning of", "what does", "stand for"]
    return any(t in q for t in triggers)


def wants_summary(question: str) -> bool:
    q = question.lower()
    return any(t in q for t in ["summarize", "tl;dr", "tldr", "in short"])