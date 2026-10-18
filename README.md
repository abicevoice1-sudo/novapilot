# NovaPilot — your personal AI pilot

NovaPilot is an independent, open-source personal AI agent: it **remembers**, **researches**, **plans**, **executes**, **learns from feedback**, and keeps working on your approved goals while you're away.

**Status: v0.8.0 — Phases A–E complete (2026-10-18).** Nova now: schedules recurring work with missed-run replay, learns from its own task history (nightly dreaming consolidation + reusable skills), talks over Telegram, consumes MCP servers, snapshots your workspace before every risky step (Time Travel revert), runs full shell commands in a locked-down Docker sandbox, and ships with prompt-injection evals. Memory (M4), browser workspace (M5), and the agent core (M3) all live. Nothing here is mocked and presented as working; `docs/roadmap.md` tracks exactly what's real, and anything unverifiable in CI is labeled honestly.

## Why NovaPilot

Twenty personal-agent projects were researched live on 2026-10-18 (`research/competitor-matrix.md`). Nobody clears 8/10. The gaps NovaPilot is built to fill:

1. **Audited autonomy with consumer UX** — signed tool receipts + tiered approvals behind a web UI nobody has built
2. **Memory you can read and own** — local-first, editable, exportable, deletable
3. **Budgets as a feature** — per-task cost/latency caps with provider fallback routing
4. **A polished web app** — every serious contender is CLI/TUI-first
5. **Honesty as a feature** — verified-vs-planned labeling; reproducible evals published from day one

## Quickstart

```bash
curl -fsSL https://raw.githubusercontent.com/abicevoice1-sudo/novapilot/master/install.sh | bash
# or: git clone https://github.com/abicevoice1-sudo/novapilot && cd novapilot && ./install.sh
```

Then:

```bash
.venv/bin/uvicorn app.main:app --app-dir services/api
# open http://localhost:8000 — the web UI is served from the API
```

No API keys required: local Ollama inference is the default, with free-tier
cloud fallbacks (Groq → Gemini → OpenRouter). Set `NOVAPILOT_TOKEN` in `.env`
to lock the API with bearer auth. See `docs/setup.md` for the full setup
(docker-compose, dev mode, verification).

## The plan

| Milestone / Phase | Scope | Status |
|-----------|-------|--------|
| 1 — Research & specification | 20-repo matrix, ADRs, threat model, cost model, roadmap, scaffold | ✅ done 2026-10-18 |
| 2 — Running foundation | FastAPI + React chat (SSE) + LiteLLM gateway (Ollama default, budgets) + persistence | ✅ done 2026-10-18 |
| 3 — Agent core | LangGraph plan→act→verify, approvals, budgets, receipts | ✅ done 2026-10-18 |
| 4 — Memory | user-owned memory (SQLite+FTS5, mem0 adapter), agent tools, chat recall, redaction | ✅ done 2026-10-18 |
| 5 — Browser workspace | Playwright + scoped nav, approval-gated actions, screenshots in UI | ✅ done 2026-10-18 |
| A — Scheduler | Recurring tasks (NL parsing, pre-approved tools, missed-run replay) | ✅ done 2026-10-18 |
| B — Learning loop | Nightly dreaming consolidation, reusable skills | ✅ done 2026-10-18 |
| C — Channels + MCP | Telegram channel, MCP stdio client, skill export/import | ✅ done 2026-10-18 |
| D — Hardening | Prompt-injection evals, workspace checkpoints (Time Travel), Docker sandbox | ✅ done 2026-10-18 |
| E — Polish + launch | Installer, docs refresh, v0.8.0 release | ✅ done 2026-10-18 |

## Cost

$0 by default: local Ollama inference, free-tier cloud fallback chain (Groq → Gemini → OpenRouter), local-first everything. See `docs/cost-model.md` for verified quotas and exhaustion behavior.

## Security

Threat model in `docs/security.md`. Report vulnerabilities privately per `SECURITY.md` — never as public issues.

## License

Apache-2.0. See `LICENSE`.
