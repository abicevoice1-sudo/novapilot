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

## Milestone 5 — Browser workspace ✅ (2026-10-18)

- [x] `novapilot-browser` package: real Chromium via Playwright (headless), lazy start
- [x] Scoped navigation (`BROWSER_ALLOWED_DOMAINS`; http(s) only)
- [x] 9 agent tools (open/snapshot/read/click/fill/select/press/back/screenshot) —
      ALL risk=high + approval-gated; every action screenshotted, receipts in the
      task event stream, screenshots served at `GET /api/shots/{name}`
- [x] Task detail UI shows per-step screenshots + latest browser view
- [x] Safety doc (`docs/browser.md`): no credential autofill, sign-in is human-takeover

**Acceptance:** the agent ran a demo flight search end-to-end on real Chromium
(open → fill origin → fill destination → submit → read results), 5 approval
gates (each approved), 4 screenshots, task completed. Verified live 2026-10-18.
Deferred: file sandbox tightening (Docker), injection evals — folded into M7.

**Acceptance:** research task produces a cited report; login flow works without the password touching the model; planted injection in a test page is refused.

## Milestone 6 — Scheduling & proactivity ✅ (2026-10-18, Phase A of #1 plan)

- [x] `novapilot-scheduler` package: natural-language parsing ("every morning at 8",
      "every monday at 9am", "every 30 minutes"), Schedule model, native asyncio
      driver over APScheduler trigger math (replaced AsyncIOScheduler after its
      fire-and-forget shutdown raced TestClient teardown)
- [x] Per-schedule `preapproved_tools` (default: none — fully supervised); every
      skip audit-logged; tasks carry `source: "schedule:<id>"`
- [x] Missed-run replay on boot; run-now without changing cadence
- [x] Schedules UI page (list/create/edit/run-now, NL/cron/interval modes)
- [ ] Proactive engine v1 (overdue nudges, deadline warnings) — Phase B

**Acceptance:** live-verified — a 20s schedule fired twice, tasks completed,
NL parsed, bad input 422'd. 9 package + 7 API tests green; full suite stable
across 5 consecutive runs (38 tests).

## Phase B — Learning loop ✅ (2026-10-18)

- [x] `novapilot-learning` package: `DreamConsolidator` (task summaries →
      durable facts via memory service, bad JSON dropped never stored),
      `SkillStore` (SKILL.md with YAML frontmatter, keyword-relevant lookup)
- [x] Planner receives relevant skills automatically (`skills_provider`
      plumbed through TaskRunner → build_graph → plan node; broken providers
      can't break planning)
- [x] API: `/api/skills` CRUD, `POST /api/dreaming/run`, `POST /api/tasks/{id}/make-skill`
- [x] Nightly dreaming auto-schedule (02:00) created on first boot
- [x] Skills UI page + "Run dreaming now" + "Make skill" button on tasks
- [x] docs/learning.md

**Acceptance:** live-verified — task completed → dreaming stored 1 fact →
fact searchable in memory → make-skill created `note-reader` SKILL.md →
planner skill matching confirmed. 9 learning + 4 API tests green.

## Phase C — Channels + MCP + skill portability ✅ (2026-10-18)

- [x] `novapilot-channels`: Telegram long-polling (getMe verification,
      unauthorized-user filtering, 4k message chunking). 5 tests (mocked API).
- [x] Channel manager: inbound → fully-supervised task (`source:
      "telegram:<chat_id>"`), "On it" ack, approval nudges, summary replies.
      `GET /api/channels` status.
- [x] `novapilot-mcp`: dependency-free MCP stdio client (initialize →
      tools/list → tools/call). MCP tools register as `mcp_<server>_<tool>`
      with risk=medium + requires_approval. 3 tests (fake server).
- [x] Skill export/import: portable SKILL.md, `GET /api/skills/{name}/export`,
      `POST /api/skills/import` (400 on garbage).
- [x] docs/channels.md; CI + Dockerfile updated.

**Acceptance:** live-verified — MCP weather server registered at boot, task
hit the approval gate for `mcp_weather_get_weather`, approved, completed with
"Sunny in Baltimore". Telegram→task→reply flow integration-tested.

## Phase D — Hardening ✅ (2026-10-18)

- [x] Prompt-injection evals (`packages/agent-core/tests/test_injection.py`,
      documented in `tests/security/`): approval-gate immunity, untrusted-data
      labeling in summarizer prompt, planner input hygiene, skill containment,
      goal injection — 5 evals, all structural (mechanisms, not model behavior)
- [x] Workspace checkpoints (Time Travel): snapshot before every approved
      risky step, `POST /api/tasks/{id}/revert` restores; `CheckpointManager`
      in agent-core, 5 unit + 2 API tests
- [x] Docker sandbox: `DockerSandbox` (no network, capped resources, read-only
      root) + `shell_sandboxed` tool (high-risk, approval-gated) registered
      only when `NOVAPILOT_SANDBOX=docker` and Docker is reachable; graceful
      fallback otherwise. 5 tests (mocked — no Docker in CI)
- [x] docs updates (security evals README, roadmap)

**Acceptance:** 39 core + 50 API tests green; injection evals prove the gates
are code-not-prompt; checkpoint revert verified via API test (approved
write_file → checkpoint_created event → revert succeeds).

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

## Phase F — Gmail + agent control ✅ (2026-10-18)

- [x] Gmail integration (`packages/gmail/`): stdlib IMAP/SMTP client,
      `gmail_list` / `gmail_read` (low risk) + `gmail_send` (high risk,
      approval-gated) agent tools, inbound channel (UNSEEN poll → fully-
      supervised tasks, sender allowlist). 7 tests, mocked IMAP/SMTP.
- [x] Global pause/resume (`POST /api/agent/pause|resume`, `GET /api/agent/status`):
      scheduler skips firing and channels ignore inbound while paused.
- [x] Quiet hours (`QUIET_HOURS_START/END`, HH:MM local): schedules don't fire
      inside the window; run-now still works. 3 control tests.

**Acceptance:** 7 gmail + 3 control tests green; 53 API tests green total;
ruff clean. Honest limits: IMAP/SMTP untested against real Gmail here
(needs a Google App Password); channel polling is 60s, not push.

## Phase G — Calendar + multi-agent ✅ (2026-10-18)

- [x] Calendar integration (`packages/calendar/`, CalDAV via `caldav` lib):
      `calendar_list` (low risk) + `calendar_create` (high risk,
      approval-gated) agent tools. Works with Google Calendar (App Password),
      Nextcloud, Fastmail, iCloud. 5 tests, mocked CalDAV.
- [x] Multi-agent delegation (`novapilot_agent/delegate.py`): `delegate` tool
      with 4 specialist roles (researcher, coder, browser_operator,
      communicator), each with a restricted toolset. Sub-agents share the
      parent's approval queue, budget, and event stream; cannot delegate
      further (no recursion). 5 tests.

**Acceptance:** 5 calendar + 5 delegate tests green; 44 core + 53 API green;
ruff clean. Honest limits: CalDAV untested against a real server here;
sub-agents are sequential (no parallel fan-out yet).

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
