# mem0ai/mem0 — research notes

- Canonical URL: https://github.com/mem0ai/mem0
- Category: [framework/component] — memory-layer library/SDK + optional self-hosted server. Not an end-user product.
- Verification date: 2026-10-18. Stats (from saved GitHub API JSON): 67,370 stars · 7,940 forks · 841 open issues · License: Apache-2.0 · Primary language: Python (JS SDK also) · Last push: 2026-10-17 · Archived: no. Latest GitHub release: unknown (no GitHub releases; versioned via PyPI `mem0ai` / npm `mem0ai`).

## What it provides as a building block
The long-term memory subsystem of a personal agent: `Memory().add()` extracts and stores memories from conversation; `Memory().search()` retrieves relevant memories (semantic + BM25 + entity linking, fused). Three deployment modes: pip/npm library (prototype), Docker Compose self-hosted server (with dashboard + auth), managed cloud platform. Has a CLI (`mem0`) and agent-coding skills (`mem0-integrate`, etc.).

## Models / providers / cost
- Requires an LLM to function; default `gpt-5-mini`, default embedder `text-embedding-3-small` (both OpenAI, paid). Docs list other LLMs/embedders; the README's recommended embedding option is the open Qwen 600M model.
- Free usage: library/OSS is free, but LLM + embedding calls cost unless pointed at free/local endpoints. Local inference status for the extraction LLM is unknown from the README.
- BYOK: yes — bring your own provider keys.

## Memory design
- This IS the memory layer. Multi-level memory (user, session, agent state), adaptive personalization, provenance not documented in README. OSS v3: single-pass ADD-only extraction (no update/delete), entity linking, multi-signal retrieval, temporal reasoning. Published benchmarks: LoCoMo 92.5, LongMemEval 94.4, BEAM(1M) 64.1 — **caveat: README states these numbers reflect the managed platform with proprietary optimizations "not available in the open-source SDK".**

## Proactive / scheduling / background
- None — app-level concern. No scheduler, cron, or proactive engine in the library.

## Browser / computer / file / terminal
- None. Integrations documented for LangGraph and CrewAI; a Chrome extension exists for storing memories from ChatGPT/Perplexity/Claude, but no automation capabilities.

## Integrations / MCP
- Integrates with LangGraph and CrewAI; Vercel AI SDK skill; self-hosted server exposes a REST API; docs reference MCP only as a docs-query server for coding assistants (not a capability MCP server for mem0 itself).

## Multi-agent
- Not an orchestration layer; memory is shared per `user_id` / `agent_id` namespaces, so multiple agents can share or partition memory.

## Voice / image / document / multimodal
- None. Stores textual memories only.

## As a dependency: install / hardware / cost / maintenance
- `pip install mem0ai` (+ optional `mem0ai[nlp]` + spaCy model for hybrid search). Self-hosted server via Docker Compose needs Qdrant + Postgres/Neo4j-ish stack and an LLM provider. Cost is dominated by LLM/embedding API calls per add/search. Maintenance: active (pushed yesterday), YC S24, 841 open issues.

## Security posture (embedding it)
- Memories are a high-value data store: self-hosted auth is on by default (`ADMIN_API_KEY`); cloud mode sends memory content to their servers and OpenAI by default — fine only if that data flow is disclosed. README claims no memory-specific prompt-injection filtering; treat retrieved memories as untrusted data (poisoning risk). Deletion/edit APIs exist in the platform; OSS API per docs.

## Strengths / weaknesses / lesson
- Strengths: (1) Purpose-built, benchmark-published memory layer — strongest category fit for this requirement. (2) Three deployment tiers (library → self-hosted → cloud) match zero-ops and self-hosted plans. (3) Entity-linked multi-signal retrieval + temporal reasoning is the state of the art for personal recall.
- Weaknesses: (1) Managed-platform benchmark numbers don't apply to the OSS SDK. (2) LLM dependency per operation adds latency + cost to every recall/write; no offline fallback documented. (3) Cloud path routes personal data through their infra; self-hosted path is heavier ops.
- Best lesson to steal: **add-only accumulation with entity linking and temporal-ranked retrieval** — never overwrite memories; resolve conflicts at retrieval time by recency + entity.

## Scores (as a building block for a personal agent)
1. Intelligence/model flexibility: 7 — model-agnostic LLM layer, but memory itself doesn't raise reasoning.
2. Persistent memory: 10 — that is exactly what it is; benchmarked at 92.5 LoCoMo / 94.4 LongMemEval (platform).
3. Autonomous execution: 2 — no execution capability at all.
4. Proactive assistance: 1 — nothing proactive; app-level.
5. Browser/computer control: 1 — none.
6. Integrations/extensibility: 7 — LangGraph/CrewAI integrations, REST API, CLI, coding-agent skills.
7. Privacy/security: 6 — self-hosted auth on by default; cloud = data leaves your infra; no stated anti-poisoning filters.
8. Ease of deployment: 7 — pip install for library; Docker Compose for server; managed for zero-ops.
9. Free-tier/local accessibility: 5 — OSS free, but default LLM/embedder calls cost; local-model path not documented.
10. Reliability/observability: 6 — benchmarked + CI; managed platform offers dashboards; OSS observability unknown.
11. Developer experience: 8 — tiny API surface (`add`/`search`), CLI, skills that teach coding agents to integrate it.
12. Community health: 9 — 67k stars, active (push 2026-10-17), YC-backed, growing docs.

## Verdict
**ADOPT** — as the long-term memory layer (self-hosted mode first), keeping an abstraction so it can be swapped if the managed-platform/OSS benchmark gap proves material.
