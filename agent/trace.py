from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable


def now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class TimedOutput:
    started_at_ms: int
    finished_at_ms: int
    output: str


def timed_call(fn: Callable[..., str], **kwargs: Any) -> TimedOutput:
    start = now_ms()
    out = fn(**kwargs)
    end = now_ms()
    return TimedOutput(started_at_ms=start, finished_at_ms=end, output=out)
