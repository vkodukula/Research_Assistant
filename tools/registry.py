from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    schema: dict
    fn: Callable[..., str]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._tools:
            raise ValueError(f"Tool already registered: {spec.name}")
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def list_schemas(self) -> list[dict]:
        """
        Function-calling-like schemas (useful for future swap-in of real LLM planners).
        """
        schemas = []
        for spec in self._tools.values():
            schemas.append(
                {
                    "type": "function",
                    "function": {
                        "name": spec.name,
                        "description": spec.description,
                        "parameters": spec.schema,
                    },
                }
            )
        return schemas

    def call(self, name: str, **kwargs: Any) -> str:
        return self.get(name).fn(**kwargs)