from __future__ import annotations

# Offline “documents” used by search_web. Extend this list to improve coverage.

KB = [
    {
        "id": "kb:langgraph:overview",
        "title": "LangGraph overview",
        "text": (
            "LangGraph models multi-step LLM applications as graphs with nodes and edges, "
            "supporting loops, branching, and stateful execution."
        ),
        "tags": ["langgraph", "graphs", "state", "orchestration"],
    },
    {
        "id": "kb:function-calling:pattern",
        "title": "Function calling pattern",
        "text": (
            "Function calling is when a model emits a structured request to call a tool "
            "(function name + JSON args). The system executes the tool and returns results "
            "to ground the final answer."
        ),
        "tags": ["function calling", "tools", "agents", "structured outputs"],
    },
    {
        "id": "kb:rag:definition",
        "title": "RAG definition",
        "text": (
            "Retrieval-Augmented Generation (RAG) retrieves relevant context before generating, "
            "improving factual grounding and enabling citations to evidence."
        ),
        "tags": ["rag", "retrieval", "citations", "grounding"],
    },
    {
        "id": "kb:citations:practice",
        "title": "Citations for tool-using assistants",
        "text": (
            "A practical citation approach is to reference the specific tool calls that produced "
            "supporting evidence, enabling auditability and debugging."
        ),
        "tags": ["citations", "provenance", "audit"],
    },
    {
        "id": "kb:agent-loop:reflect",
        "title": "Agent loop with reflection",
        "text": (
            "A common agent structure is plan → act → observe → reflect. Reflection checks if evidence is sufficient; "
            "if not, the agent gathers more information or asks clarifying questions."
        ),
        "tags": ["agent", "loop", "reflection", "planning"],
    },
]