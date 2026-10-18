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

## Milestone 2 — Running foundation

- [ ] FastAPI service: config, SQLite/Postgres, auth, health, structured logging
- [ ] React UI shell: chat interface (streaming), navigation, settings pages
- [ ] Model gateway live: LiteLLM with Ollama default + Groq/Gemini fallback chain
- [ ] `docker-compose up` brings the whole thing up; `docs/setup.md` verified on a clean machine
- [ ] CI: lint, typecheck, unit tests

**Acceptance:** clean-machine `docker-compose up` → chat with a local model works end to end; no key required.

## Milestone 3 — Agent core

- [ ] LangGraph plan→act→verify loop; tool registry with JSON-schema validation
- [ ] Task states (active/paused/failed/completed), cancellation, bounded retries
- [ ] Approval gates via graph interrupts; signed tool receipts in audit log
- [ ] Per-task budgets (tokens/calls/cost/time) enforced by the gateway

**Acceptance:** a 5-step task runs with streaming tool activity; killing it mid-run leaves a clean, resumable state; a budget breach pauses with an explanation.

## Milestone 4 — Memory

- [ ] mem0 self-hosted wired in; conversation history persisted
- [ ] Provenance (source/timestamp/confidence) on every memory; user review/edit/delete UI
- [ ] Markdown mirror (`USER.md`/`MEMORY.md`); export + full wipe flows
- [ ] Recall across restarts tested

**Acceptance:** preference saved in session N is recalled in session N+2 after a restart; user can inspect, edit, and delete it.

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
