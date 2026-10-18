# langchain-ai/langgraph — research notes

- Canonical URL: https://github.com/langchain-ai/langgraph
- Category: [framework/component] — low-level orchestration library for stateful agents/workflows. Not an end-user product.
- Verification date: 2026-10-18. Stats (from saved GitHub API JSON): 43,426 stars · 7,401 forks · 651 open issues · License: MIT · Primary language: Python (LangGraph.js is a separate repo) · Last push: 2026-10-18 · Archived: no. Latest GitHub release: **1.2.16 (2026-10-16)** — verified via releases API.

## What it provides as a building block
The execution/runtime substrate of a personal agent: graphs of nodes with typed state, durable execution (checkpointing, resume-after-failure via checkpointer stores), human-in-the-loop interrupts (inspect/modify state mid-run — the approval-gate primitive), short-term working memory + long-term cross-session memory (stores), and subgraphs/subagents for decomposition. Higher-level `deepagents` package (plan + subagents + filesystem) sits on top. Deployment via LangSmith Deployment; debugging via LangSmith traces.

## Models / providers / cost
- Model-agnostic: works with any chat model through LangChain model integrations; README does not enumerate providers. Fully BYOK (user's own keys; no LangChain account required to use the library).
- Free usage: library is 100% free/OSS (MIT). LangSmith observability and LangSmith Deployment are paid managed services (free tier unknown — not stated in README).
- Local inference: not documented in README; depends on the chosen model integration (Ollama-backed chat models exist in the LangChain ecosystem — unverified here, so marked as: works with whatever model client you supply).

## Memory design
- Built-in persistence layer: thread-scoped checkpointing (short-term/stateful conversation) + long-term memory stores across sessions. This is operational/state memory, not a semantic personal-knowledge layer — pair with mem0-style retrieval for personal recall.

## Proactive / scheduling / background
- Partial: durable execution supports long-running workflows and resume; "run for extended periods". No built-in cron/scheduler in the README — scheduling is app-level (e.g. trigger runs from cron and checkpoint state). No proactive notification engine.

## Browser / computer / file / terminal
- None built in; provided via tools the developer attaches. `deepagents` adds filesystem access for agents. Browser/computer use comes from MCP servers or custom tools wired as graph nodes.

## Integrations / MCP
- MCP support exists in the broader LangChain/LangGraph ecosystem (tool adapters), and LangSmith deployment + Studio; README frames LangGraph as usable standalone or with LangChain integrations.

## Multi-agent
- Yes — native: subgraphs, parallel branches, supervisor-style patterns, and the `deepagents` subagent layer. Pregel-inspired message-passing model.

## Voice / image / document / multimodal
- None built in; multimodal depends on the attached model/tools.

## As a dependency: install / hardware / cost / maintenance
- `pip install -U langgraph`; zero infrastructure for the library itself (state stores are pluggable: SQLite default → Postgres for prod). Cost = whatever the model provider charges. Maintenance: very active (push today, release 2 days ago), LangChain Inc backing, 651 open issues on a large user base.

## Security posture (embedding it)
- Human-in-the-loop interrupts are the framework-native approval-gate primitive (strong for the "approve consequential actions" requirement). Code/tools execute wherever the developer runs them — sandboxing is the developer's job. No stated prompt-injection framework; tool outputs are developer-managed data. LangSmith (cloud) receives traces if enabled — a data-exposure surface to disclose.

## Strengths / weaknesses / lesson
- Strengths: (1) Durable execution + checkpointing + resume is exactly the "resume interrupted work" requirement. (2) Human-in-the-loop interrupts are the cleanest approval-gate primitive among all frameworks reviewed. (3) Low-level and unopinionated — no forced agent persona or cloud lock-in; MIT license.
- Weaknesses: (1) It's a runtime, not a product — chat UI, scheduling, proactive engine, model gateway, and memory semantics must all be built. (2) Heavier conceptual model (graphs/state/reducers) than needed for a single personal agent; over-engineering risk. (3) Best observability (LangSmith) is a paid cloud service.
- Best lesson to steal: **checkpointer-based durable execution with human-in-the-loop interrupts** — every long task should be resumable, and every consequential tool call should be pausable for approval.

## Scores (as a building block for a personal agent)
1. Intelligence/model flexibility: 9 — fully model-agnostic; any chat model client plugs in.
2. Persistent memory: 7 — strong operational/state memory (checkpoints + long-term stores); not a semantic personal-memory layer.
3. Autonomous execution: 8 — durable, resumable, long-running graph execution with subagents.
4. Proactive assistance: 3 — no scheduler or notification engine; resume/long-run primitives only.
5. Browser/computer control: 3 — no built-ins; enables via attached tools/MCP.
6. Integrations/extensibility: 9 — MCP/tool adapters, LangChain ecosystem, deepagents, deployment platform.
7. Privacy/security: 7 — HITL interrupts native; sandboxing left to developer; LangSmith cloud surface.
8. Ease of deployment: 7 — pip + pluggable stores; managed deployment optional.
9. Free-tier/local accessibility: 8 — MIT, free library, local SQLite; paid bits (LangSmith) optional.
10. Reliability/observability: 8 — durable execution + LangSmith traces; local observability without LangSmith is thinner.
11. Developer experience: 8 — well-documented, Academy courses, typed state, visual Studio prototyping.
12. Community health: 10 — 43k stars, daily pushes, LangChain Inc maintained, used by Klarna/Replit/Elastic per README.

## Verdict
**ADOPT** — as the agent runtime/orchestration core (durable execution + HITL approvals + subgraphs), with a thin model-gateway and scheduler built on top rather than taken from it.
