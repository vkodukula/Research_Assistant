# Tool-Using Research Assistant (Offline) — LangGraph + LangChain Core

## Overview

This repository contains a **tool-using research assistant** implemented in Python. It answers user questions by:

* **Deciding whether external information is needed**
* **Calling tools** when appropriate
* **Synthesizing a final answer with citations**
* Producing a complete **tool usage log** (tool name, inputs, outputs, identifiers, and timing)

This implementation is intentionally **offline** and uses **stubbed tools** (no real web access required). It still demonstrates realistic agent behavior and orchestration using **LangGraph**, and it is structured so a real LLM/function-calling backend can be swapped in later without rewriting the workflow.

---

## Deliverables Included

* **Source code in a single repository/folder**
* **README (this file)** containing:

  * How to install and run
  * Approach and architecture overview
  * Assumptions and limitations
  * Best practices followed (optional but encouraged)
  * Time spent and what would be done next with more time
  * Demo section with example input queries and example outputs showing tool usage and citations

---

## How to Install and Run

### Requirements

* Python **3.10+**
* Works on macOS / Linux / Windows
* No API keys required

### Installation

1. Create a virtual environment:

```bash
python -m venv .venv
```

2. Activate the environment:

* macOS / Linux:

```bash
source .venv/bin/activate
```

* Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Quick verification (optional):

```bash
python -c "import langgraph; import langchain_core; import pydantic; print('ok')"
```

### Running

Run the CLI:

```bash
python main.py
```

Optional flags:

* Print full tool outputs (no truncation):

```bash
python main.py --full-log
```

* Increase the maximum number of agent loop iterations (bounded; default = 2):

```bash
python main.py --max-iterations 3
```

### What the CLI prints

For each user query, the CLI prints:

1. **PLAN** — the steps the agent intends to follow
2. **FINAL ANSWER** — the synthesized response with citations
3. **TOOL USAGE LOG** — tools called with args, outputs, and timing

---

## Approach and Architecture Overview

### High-Level Approach

The assistant is implemented as a **graph-based agent loop** using **LangGraph**. The agent operates in stages:

1. Plan what to do
2. Call tools if needed
3. Observe tool outputs
4. Reflect whether evidence is sufficient
5. Optionally gather more evidence (bounded loop)
6. Synthesize a final answer with citations and an audit log

### Why LangGraph?

LangGraph makes multi-step agents easier to reason about because you can:

* Represent each step as a node
* Make routing decisions via conditional edges
* Maintain explicit state across steps
* Bound iteration to prevent runaway loops

This directly matches the “tool-using research assistant” problem.

---

## Architecture Details

### Graph Nodes (Workflow)

The workflow is modeled as the following nodes:

1. **Planner**

* Parses the question
* Extracts key terms (e.g., “rag”, “langgraph”)
* Decides which tools are necessary using lightweight heuristics
* Produces:

  * a human-readable plan
  * a list of structured tool calls (tool name, args, unique call id)

2. **Act (Tool Execution)**

* Executes proposed tool calls via a centralized tool registry
* Records structured results including:

  * call id
  * tool name
  * tool args
  * tool output
  * start/end timestamps (duration)

3. **Reflect**

* Checks whether the question type requires evidence and whether evidence exists
* If evidence is missing or empty, triggers another evidence pass (bounded)

4. **More Evidence (Optional)**

* Creates a more targeted query (e.g., original question + “overview examples tradeoffs”)
* Calls `search_web` again
* Returns to Act

5. **Final**

* Synthesizes a final response using gathered tool outputs
* Attaches citations to all tool-derived statements
* Produces confidence + limitations
* Summarizes tool usage in the final answer (and the CLI prints the full tool log)

### State Management

The agent uses a single explicit state object passed between nodes. It includes:

* `user_question` — the raw query
* `plan` — steps the agent intends to take
* `tool_calls` — pending tool requests (name + args + id)
* `tool_results` — completed results from tools
* `iteration` and `max_iterations` — loop control
* `needs_more_evidence` — reflection result
* `final` — the final answer object (text + citations + confidence + limitations)
* `tool_log` — append-only audit log of all tool executions

Explicit state ensures clarity and makes the agent easy to debug and extend.

---

## Tool Model and Tool Registry

### Tools Implemented (Stubbed/Offline)

This project implements **3 tools**:

1. `search_web(query, k=3)`

* Searches a small local KB (offline corpus)
* Returns top-k ranked snippets
* Includes KB document provenance (`doc_id`) in the output

2. `lookup_definition(term)`

* Returns a definition from a hardcoded dictionary

3. `summarize(text, max_sentences=2)`

* Rule-based summarizer to keep outputs short
* Used only if the user explicitly requests a summary

### Tool Registry

Tools are registered in a centralized registry that stores:

* tool name
* description
* JSON schema (function-calling style)
* Python implementation

Why this matters:

* It cleanly separates **agent logic** from **tool implementations**
* It is easy to add tools without changing the graph
* It makes swapping in a real function-calling LLM easier later (schemas already exist)

---

## Citations

The final answer includes citations to the tool calls used.

### Citation format

```text
[source: TOOL_NAME#CALL_ID]
```

Example:

* `[source: search_web#call_0002]`

Citations are tied to tool invocation IDs so a reviewer can trace:

* which tool produced the evidence
* which invocation (call id)
* which args were used
* what output was returned

---

## Tool Usage Log

Every tool call is logged with:

* tool name
* call id
* args
* output (preview or full output)
* execution duration (ms)

The CLI prints a full log after every query. The final answer also includes a brief summary of sources used.

This satisfies the requirement: “log tool usage (which tools were called, with what inputs, and returned outputs or identifiers).”

---

## Assumptions and Limitations

* **No real web access**: `search_web` is offline and searches a small KB only.
* Planner and reflection are **deterministic heuristics**, not a hosted LLM.
* Answer quality depends on KB coverage; expanding the KB improves retrieval.
* Citations reference tool calls (and KB doc IDs embedded in outputs), not external URLs.

These are intentional choices to keep dependencies minimal and align with the assignment’s “mock/stub tools allowed” constraint.

---

## Best Practices Followed (Optional but Included)

* Minimal and justified dependencies (LangGraph, LangChain Core, Pydantic)
* Clear module separation:

  * orchestration (graph)
  * state model
  * policies (decisions)
  * tools (implementations)
  * tool registry (schemas + dispatch)
* Explicit state passing for traceability
* Bounded iterations to prevent infinite loops
* Auditability via:

  * tool logs
  * stable call ids
  * citations referencing tool calls
* Extensible design: add tools or replace heuristics with an LLM without rewriting everything

---

## Time Spent

Designed to fit within the requested **~3–4 hour** time box by focusing on:

* clear orchestration and routing
* correct tool usage discipline
* citations and logging
* readable organization and documentation

---

## What I Would Do Next With More Time

* Add a local-file retrieval tool (true RAG over a folder of `.md`/`.txt` files)
* Improve retrieval ranking (BM25-style scoring) while staying lightweight
* Add unit tests for:

  * planner routing decisions
  * tool registry dispatch
  * reflection branching behavior
  * citation formatting invariants
* Swap the heuristic planner with a real function-calling LLM or local model
* Add claim-level citation enforcement (each paragraph must cite evidence or be explicitly marked as inference)

---

## Demo: Example Queries and Outputs

> Note: call IDs are generated at runtime and may differ. The structure and citation format will match.

### Demo 1 — Tool usage + citations

**Input**

```text
What is LangGraph and why would I use it?
```

**Example Output (excerpt)**

```text
## Evidence (offline search)
- LangGraph models multi-step LLM applications as graphs with nodes and edges... [source: search_web#call_0001]

## Answer
LangGraph is most useful when you want explicit, stateful control over multi-step workflows: branching, loops, and clear execution structure...

Citations: [source: search_web#call_0001]
```

**Tool Usage Log (excerpt)**

```text
- search_web  id=call_0001
  args: {"query": "What is LangGraph and why would I use it?", "k": 3}
  output: 1. LangGraph overview (doc_id=kb:langgraph:overview) — ...
  duration_ms: 1
```

---

### Demo 2 — Multiple tools + multiple citations

**Input**

```text
Define RAG and explain why it helps with hallucinations.
```

**Example Output (excerpt)**

```text
## Definitions
- rag: Retrieval-Augmented Generation... [source: lookup_definition#call_0001]

## Evidence (offline search)
- Retrieval-Augmented Generation (RAG) retrieves relevant context... [source: search_web#call_0002]

## Answer
RAG helps because it grounds generation in retrieved context, enabling more faithful answers and citations to supporting evidence.

Citations: [source: lookup_definition#call_0001] [source: search_web#call_0002]
```

**Tool Usage Log (excerpt)**

```text
- lookup_definition id=call_0001
  args: {"term": "rag"}
  output: Retrieval-Augmented Generation...

- search_web id=call_0002
  args: {"query": "Define RAG and explain why it helps with hallucinations.", "k": 3}
  output: 1. RAG definition (doc_id=kb:rag:definition) — ...
```

---

### Demo 3 — Reflection + retry (bounded loop)

**Input**

```text
Compare LangChain and LangGraph. When would you choose one over the other?
```

**Example Behavior**

* Planner triggers evidence search (`search_web`)
* Reflect checks for sufficient evidence
* If evidence is missing/empty, the agent triggers a targeted follow-up search:

  * query appended with `overview examples tradeoffs`
* Loop stops at `max_iterations`

**Citations**

The final response will cite the search tool call(s), e.g.:

* `[source: search_web#call_0001]`
* `[source: search_web#call_0002]` (if retry occurs)

---

## Evaluation Criteria Alignment

### Clarity

* Explicit state model
* Clear naming and file organization
* README explains what each major component does

### Simplicity

* Minimal dependencies, all justified
* Offline tools are deterministic and easy to inspect
* No unnecessary complexity, no UI, no external services

### Extensibility

* Tools isolated behind a registry
* Agent logic separated from tool implementations
* Easy to add tools, refine decision-making, or swap in a real LLM later