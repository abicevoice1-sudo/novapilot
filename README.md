# NovaPilot — your personal AI pilot

NovaPilot is an independent, open-source personal AI agent: it **remembers**, **researches**, **plans**, **executes**, **learns from feedback**, and keeps working on your approved goals while you're away.

**Status: Milestone 1 — research & specification (2026-10-18).** This repo currently contains the full 20-repository competitor research, architecture decisions, threat model, cost model, and roadmap — plus a runnable API skeleton. The agent itself is built across Milestones 2–8 (see `docs/roadmap.md`). Nothing here is mocked and presented as working; `docs/roadmap.md` tracks exactly what's real.

## Why NovaPilot

Twenty personal-agent projects were researched live on 2026-10-18 (`research/competitor-matrix.md`). Nobody clears 8/10. The gaps NovaPilot is built to fill:

1. **Audited autonomy with consumer UX** — signed tool receipts + tiered approvals behind a web UI nobody has built
2. **Memory you can read and own** — local-first, editable, exportable, deletable
3. **Budgets as a feature** — per-task cost/latency caps with provider fallback routing
4. **A polished web app** — every serious contender is CLI/TUI-first
5. **Honesty as a feature** — verified-vs-planned labeling; reproducible evals published from day one

## Quickstart (Milestone 2 target)

```bash
cp .env.example .env        # no keys required — Ollama default
docker-compose up           # api + worker + browser sandbox
# open http://localhost:8000 → chat with a local model
```

Today (Milestone 1), the skeleton proves the shape:

```bash
cd services/api && pip install -e .  # or: uv sync
uvicorn app.main:app --reload        # GET /health → {"ok": true, ...}
```

## The plan

| Milestone | Scope | Status |
|-----------|-------|--------|
| 1 — Research & specification | 20-repo matrix, ADRs, threat model, cost model, roadmap, scaffold | ✅ done 2026-10-18 |
| 2 — Running foundation | FastAPI + React chat + LiteLLM gateway (Ollama default) | next |
| 3 — Agent core | LangGraph plan→act→verify, approvals, budgets, receipts | planned |
| 4 — Memory | mem0 self-hosted + provenance + markdown mirror + export/delete | planned |
| 5 — Browser & files | Playwright module, sandboxed files, injection evals | planned |
| 6 — Scheduling & proactivity | Persistent scheduler, quiet hours, global pause | planned |
| 7 — Integrations & multi-agent | Channels, skills, specialist subagents | planned |
| 8 — Quality & release | Full test suites, published evals, v1.0.0 | planned |

## Cost

$0 by default: local Ollama inference, free-tier cloud fallback chain (Groq → Gemini → OpenRouter), local-first everything. See `docs/cost-model.md` for verified quotas and exhaustion behavior.

## Security

Threat model in `docs/security.md`. Report vulnerabilities privately per `SECURITY.md` — never as public issues.

## License

Apache-2.0. See `LICENSE`.
