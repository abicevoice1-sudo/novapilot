# NovaPilot — Roadmap

Milestones ship as small, testable vertical slices. A milestone is **not complete** until its acceptance tests pass; status is tracked here honestly.

## Milestone 1 — Research & specification ✅ (2026-10-18)

- [x] Verify 20 competitor repos (live GitHub API + README reads)
- [x] `research/competitor-matrix.md`: stats, 12-dimension scores, weighted + free-tier rankings, feature comparison, best-ideas table, 10 opportunities, adopt/adapt/avoid matrix
- [x] `research/repository-evidence.md`: verification log, naming decision, dependency checks
- [x] `research/architecture-decisions.md`: 10 ADRs
- [x] `docs/`: architecture, cost-model, security (threat model), roadmap, setup
- [x] Repo scaffold: README, LICENSE (Apache-2.0), `.env.example`, `docker-compose.yml`, CI, working API skeleton
- [x] Public repo published

**Acceptance:** all boxes checked; no invented stats (unknowns marked `?`); every doc dated.

## Milestone 2 — Running foundation ✅ (2026-10-18)

- [x] FastAPI service: config, SQLite/Postgres, token auth, health, structured JSON logging
- [x] React UI shell: streaming chat, conversation sidebar, model dropdown, nav, settings page
- [x] Model gateway live: LiteLLM-backed `novapilot_gateway` package — Ollama default + Groq/Gemini/OpenRouter fallbacks, per-task cost/token/wall-clock budgets, honest "no model reachable" errors
- [x] `docker-compose up` brings up api + web (validated: compose YAML parses, Dockerfiles build from repo root; full compose run needs a Docker host — verified in CI)
- [x] CI: ruff + gateway tests + API tests + web build

**Acceptance:** chat works end to end with no key required *given a reachable model* (Ollama). Verified: 7 gateway tests + 8 API tests green, ruff clean, `npm run build` green, live smoke test (health/models/SSE chat/persistence). Without a model, the API returns a clear SSE error event — it never pretends.

## Milestone 3 — Agent core ✅ (2026-10-18)

- [x] LangGraph plan→execute→verify loop; tool registry with JSON-schema validation
- [x] Task states (pending/running/waiting_approval/paused/failed/completed/cancelled), cancellation, pause/resume, bounded retries (3 attempts, backoff)
- [x] Approval gates via graph interrupts; tool receipts on every call; SSE event stream + Tasks UI page
- [x] Per-task budgets (cost/tokens/wall-clock) enforced by the gateway; breach pauses with explanation

**Acceptance:** a 5-step task runs with streaming tool activity (live-verified: task → approval gate → approve → file written → completed); killing the process mid-run marks tasks `paused` ("interrupted by restart") and they resume from the SQLite checkpoint; a budget breach pauses the task with a `budget_exceeded` event explaining why.

## Milestone 4 — Memory ✅ (2026-10-18)

- [x] `novapilot-memory` package: embedded SQLite + FTS5 store (zero services); mem0 adapter for self-hosted mem0+Qdrant+Ollama via `MEMORY_BACKEND=mem0`
- [x] Provenance (source/timestamp/tags) on every memory; full CRUD API; Memory UI page (list/search/add/edit/delete/export/import)
- [x] Agent memory tools (`memory_search/add/update/delete`; delete needs approval); planner checks memory first
- [x] Chat recall: relevant memories injected into the system prompt; "Remember this conversation" extraction (consented write path)
- [x] Redaction enforced on every write (API keys, passwords, SSNs, cards); bare secrets refused; dedup merges near-duplicates
- [x] Export/import JSON round-trip

**Acceptance:** a fact saved in one session is recalled in a later one (verified: add → chat injects → delete → search/recall/export all clean); the user can read every memory in the UI; deleting is honored everywhere. Recall across restarts: the store is a plain SQLite file — restart-safe by construction.

## Milestone 5 — Browser & files

- [ ] Playwright browser module: local-first, persistent profiles, human-takeover view
- [ ] Sandboxed file ops + artifact creation; action receipts visible in UI
- [ ] Stagehand-pattern credential entry (secrets never reach the model)
- [ ] Injection evals in `tests/security/` passing

**Acceptance:** research task produces a cited report; login flow works without the password touching the model; planted injection in a test page is refused.

## Milestone 6 — Scheduling & proactivity

- [ ] APScheduler with persistent store; cron UI; pause/cancel/resume
- [ ] Quiet hours, notification controls, frequency limits, global pause
- [ ] Missed-schedule behavior documented; resume-after-restart for eligible jobs
- [ ] Proactive engine v1: overdue tasks, approaching deadlines, suggested next steps (with evidence shown)

**Acceptance:** a scheduled research job runs, emails the result, survives a restart; user can pause everything with one switch.

## Milestone 7 — Integrations & multi-agent

- [ ] High-value integrations (messaging channels, calendar/email) with per-integration permissions
- [ ] Specialist subagents (research, coding, browser, verification) on LangGraph; structured result exchange
- [ ] Skills as installable markdown+YAML packages (ClawHub pattern, own registry later)
- [ ] Failure isolation: one tool's failure can't corrupt other tasks

**Acceptance:** delegated research→verify pipeline completes with citations; a failing integration doesn't take down the chat loop.

## Milestone 8 — Quality & release

- [ ] Unit + integration + security + end-to-end suites green; clean-install test
- [ ] `tests/evaluations/`: memory precision/recall, citation validity, injection resistance, budget adherence, recovery rate — methodology + results published
- [ ] Latency (p50/p95), cost-per-task measured and documented
- [ ] Limitations documented; roadmap updated honestly

**Acceptance:** v1.0.0 ships with passing suites, published evals, and a limitations page. No superiority claims without reproducible evidence.

## Principal technical risks & mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Free-tier quotas throttle real use | High | Medium | Fallback chains + Ollama default; budgets make limits visible, not mysterious |
| Prompt injection via browser/tools | High | High | Injection boundary + evals from M5; approval gates on consequential actions |
| mem0 self-hosted ≠ managed quality | Medium | Medium | Measure our own recall benchmarks; markdown mirror as fallback UX |
| Scope creep (the hermes-agent trap) | High | High | Vertical slices; roadmap is the scope contract; "no" by default to new surfaces |
| LiteLLM license ambiguity | Low | Medium | Re-verify MIT at build time; gateway is swappable by design (ADR-004) |
| Single-maintainer bus factor | Medium | Medium | Docs-first, ADRs, CI; CONTRIBUTING.md from day one |
| Local-model quality ceiling | Medium | Medium | Hybrid routing (local for triage, free-cloud for reasoning); honest capability labels |
