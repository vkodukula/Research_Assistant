from __future__ import annotations

from tools.registry import ToolRegistry, ToolSpec
from tools.implementations import search_web, lookup_definition, summarize


def build_default_registry() -> ToolRegistry:
    reg = ToolRegistry()

    reg.register(
        ToolSpec(
            name="search_web",
            description="Offline KB search. Use when you need evidence or factual grounding.",
            schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "k": {"type": "integer", "minimum": 1, "maximum": 10, "default": 3},
                },
                "required": ["query"],
            },
            fn=search_web,
        )
    )

    reg.register(
        ToolSpec(
            name="lookup_definition",
            description="Lookup a definition from a hardcoded dictionary.",
            schema={
                "type": "object",
                "properties": {"term": {"type": "string"}},
                "required": ["term"],
            },
            fn=lookup_definition,
        )
    )

    reg.register(
        ToolSpec(
            name="summarize",
            description="Rule-based summarization (minimal dependencies).",
            schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "max_sentences": {"type": "integer", "minimum": 1, "maximum": 5, "default": 2},
                },
                "required": ["text"],
            },
            fn=summarize,
        )
    )

    return reg