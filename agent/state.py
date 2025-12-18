from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    id: str
    name: str
    args: Dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    id: str
    name: str
    args: Dict[str, Any]
    output: str
    started_at_ms: int
    finished_at_ms: int

    @property
    def duration_ms(self) -> int:
        if self.started_at_ms and self.finished_at_ms:
            return max(0, self.finished_at_ms - self.started_at_ms)
        return 0


class Citation(BaseModel):
    tool: str
    call_id: str


class FinalAnswer(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    confidence: str = "medium"  # low/medium/high
    limitations: List[str] = Field(default_factory=list)


class AgentState(BaseModel):
    # Input
    user_question: str

    # Planning + tool usage
    plan: List[str] = Field(default_factory=list)
    tool_calls: List[ToolCall] = Field(default_factory=list)
    tool_results: List[ToolResult] = Field(default_factory=list)

    # Control loop
    iteration: int = 0
    max_iterations: int = 2
    needs_more_evidence: bool = False

    # Output
    final: Optional[FinalAnswer] = None

    # Audit log (append-only)
    tool_log: List[ToolResult] = Field(default_factory=list)