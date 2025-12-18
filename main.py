from __future__ import annotations

import argparse
import json
from dotenv import load_dotenv

from agent.graph import build_graph
from agent.state import AgentState


def _print_plan(plan: list[str]) -> None:
    print("\n=== PLAN ===")
    for i, step in enumerate(plan, 1):
        print(f"{i}. {step}")
    print("============\n")


def _print_tool_log(tool_log: list[dict], full: bool = False) -> None:
    print("\n=== TOOL USAGE LOG ===")
    for r in tool_log:
        print(f"- {r['name']}  id={r['id']}")
        print(f"  args: {json.dumps(r['args'], ensure_ascii=False)}")
        out = r["output"]
        if not full and len(out) > 500:
            out = out[:500] + "…"
        print(f"  output: {out}")
        dur = r.get("duration_ms")
        if dur is not None:
            print(f"  duration_ms: {dur}")
    print("======================\n")


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Offline Tool-Using Research Assistant (LangGraph).")
    parser.add_argument("--full-log", action="store_true", help="Print full tool outputs.")
    parser.add_argument("--max-iterations", type=int, default=2, help="Max agent loop iterations (default 2).")
    args = parser.parse_args()

    graph = build_graph()

    print("Offline Tool-Using Research Assistant (LangGraph). Type 'exit' to quit.\n")

    while True:
        q = input("You: ").strip()
        if not q:
            continue
        if q.lower() in {"exit", "quit"}:
            break

        state = AgentState(user_question=q, max_iterations=args.max_iterations)
        out = graph.invoke(state.model_dump())

        _print_plan(out["plan"])
        print(out["final"]["answer"])
        _print_tool_log(out["tool_log"], full=args.full_log)


if __name__ == "__main__":
    main()