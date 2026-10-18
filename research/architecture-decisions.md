# Architecture Decision Records

## ADR-001 — Python + FastAPI backend (2026-10-18)

**Decision:** Backend in Python 3.12 with FastAPI.
**Context:** The strongest building blocks are Python (LangGraph, mem0, Playwright-Python, LiteLLM). The agent ecosystem's center of gravity is Python.
**Alternatives:** TypeScript server (matches openclaw/stagehand; weaker agent-library ecosystem).
**Consequences:** One language for agent runtime, tools, and API. Accept Python's packaging complexity; mitigate with `uv` + Docker.

## ADR-002 — LangGraph as the agent runtime (2026-10-18)

**Decision:** Adopt LangGraph for agent orchestration.
**Context:** We need durable execution, checkpointing, and human-in-the-loop interrupts (the approval-gate primitive). Research verdict: ADOPT (43k★, MIT, model-agnostic, maintained).
**Alternatives:** Hand-rolled loop (more control, months of work); CrewAI (telemetry default-on, weaker memory, duplicates this role).
**Consequences:** LangSmith's paid bits stay optional; persistence via our own checkpointer (SQLite/Postgres).

## ADR-003 — mem0 (self-hosted) as the memory layer (2026-10-18)

**Decision:** Adopt mem0 in self-hosted mode for the memory subsystem, fronted by our own provenance/editing API.
**Context:** Best OSS memory primitive (add/search, entity linking, temporal ranking). Its published benchmarks reflect the managed platform — we self-host and measure ourselves.
**Alternatives:** Hand-built SQLite FTS5 + embeddings (simpler, but we'd re-derive mem0's retrieval lessons); Letta's stack (cloud-default).
**Consequences:** Memory stays local-first. We add what mem0 lacks: user-editable markdown mirror (nanobot pattern), provenance/confidence metadata, export/delete workflows.

## ADR-004 — LiteLLM as the model gateway (2026-10-18)

**Decision:** Adopt LiteLLM for the provider-neutral gateway (routing, fallbacks, retries, cost tracking).
**Context:** 61k★, actively maintained, 100+ providers, OpenAI-compatible interface. Building a gateway from scratch is the classic NIH trap the decision matrix forbids.
**Alternatives:** Hand-built adapters (full control, large surface); OpenRouter-only (single-vendor dependence).
**Consequences:** Provider logic stays out of the agent core (ACP-style neutrality). Re-verify its MIT license at build time (API returned NOASSERTION).

## ADR-005 — SQLite first, Postgres optional (2026-10-18)

**Decision:** SQLite (via aiosqlite) is the default datastore; Postgres is a config switch for multi-user deployments.
**Context:** Single-user MVP must install with zero infrastructure. No heavyweight infra without demonstrated benefit.
**Alternatives:** Postgres-only (ops burden for a laptop install); embedded DuckDB (weaker ecosystem for queues).
**Consequences:** One code path, two backends. Migration scripts from day one.

## ADR-006 — React + Vite + Tailwind frontend (2026-10-18)

**Decision:** Web UI in React 18 + Vite + Tailwind, served as static build by the API service.
**Context:** Mature, huge hiring pool, excellent component ecosystem. The empty slot in the market is a polished web app — this is where we differentiate on UX.
**Alternatives:** Next.js (heavier than needed for a local-first app); HTMX (weaker for streaming tool activity).
**Consequences:** Frontend stays a thin client; all secrets and model keys remain server-side, never in the browser.

## ADR-007 — Apache-2.0 license (2026-10-18)

**Decision:** License the project under Apache License 2.0.
**Context:** All adopted dependencies are MIT/Apache-2.0 compatible. Apache-2.0 adds an explicit patent grant over MIT, which matters for an agent project that may attract corporate contributors. Avoided: AGPL-3.0 (khoj — copyleft would infect the project), GPL-3.0 (nanoMuse).
**Consequences:** Permissive commercial use; contributors grant patent rights. No copyleft contamination.

## ADR-008 — Project name: NovaPilot (2026-10-18)

**Decision:** Product name **NovaPilot**; repo/package `novapilot`; default agent name "Nova".
**Context:** Working name NOVA collides: `nova-agent` is taken on PyPI and npm and 1,490 GitHub repos match. `novapilot` is free on PyPI, npm, and effectively free on GitHub (18 matches, all 0★).
**Consequences:** Keep the NOVA identity (agent answers to Nova) while owning a distinctive, searchable name.

## ADR-009 — Docker-sandboxed tool execution with allowlists (2026-10-18)

**Decision:** Code/file tools execute in Docker containers with network allowlists; browser runs in a dedicated Playwright container; destructive actions require approval gates.
**Context:** Adapted from ironclaw's sandbox pipeline and zeroclaw's tiered autonomy. No un-sandboxed host exec in the default configuration.
**Alternatives:** WASM sandbox (ironclaw's approach — revisit if Docker proves too heavy); host exec (rejected: unsafe default).
**Consequences:** Docker is a setup dependency; provide a restricted no-Docker mode with reduced capabilities, clearly labeled.

## ADR-010 — Scheduler: APScheduler now, durable queue later (2026-10-18)

**Decision:** Milestone 6 ships APScheduler with a persistent job store (the khoj-proven pattern); graduate to a durable task queue only when missed-schedule replay and multi-worker needs are demonstrated.
**Context:** Avoids premature infrastructure. The known gap (nanobot's missed schedules not replayed) is a documented MVP limitation with a migration path.
**Consequences:** Single-worker scheduling at first; roadmap tracks the queue migration explicitly.
