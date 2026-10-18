# NovaPilot — Architecture

**NovaPilot** is a personal AI agent: it remembers, researches, plans, executes, learns from feedback, and keeps working on approved goals while you're away. One user, local-first, provider-neutral.

## The stack (and why — see `research/architecture-decisions.md` for ADRs)

| Layer | Choice | Why |
|---|---|---|
| Agent runtime | **LangGraph** (Python) | Durable execution, checkpointing, human-in-the-loop interrupts = approval gates for free |
| Model gateway | **LiteLLM** | 100+ providers, fallbacks, retries, cost tracking; no NIH gateway |
| Memory | **mem0 self-hosted** + markdown mirror | Best OSS memory primitive; we add provenance, editing, export/delete |
| API | **FastAPI** (Python 3.12) | Async, typed, huge ecosystem |
| Database | **SQLite** default, **Postgres** optional | Zero-infra laptop install; one code path, two backends |
| Scheduler | **APScheduler** (persistent store) | Khoj-proven pattern; durable queue only when earned |
| Browser | **Playwright** in dedicated container | Mature substrate; browser-use/stagehand patterns adapted as tool modules |
| Sandbox | **Docker** + network allowlists | IronClaw-inspired pipeline; no un-sandboxed host exec by default |
| Frontend | **React 18 + Vite + Tailwind** | The empty market slot is a polished web app — this is where we win UX |
| Packaging | **Docker Compose** + `pip install novapilot` | One-command local setup |

```
                    ┌─────────────────────────────────────────┐
                    │              Web UI (React)             │
                    │  chat · tasks · memory · scheduler ·    │
                    │  browser view · costs · security · logs │
                    └───────────────────┬─────────────────────┘
                                        │ HTTPS (local)
                    ┌───────────────────▼─────────────────────┐
                    │            FastAPI service              │
                    │  auth · approvals · audit log · budgets │
                    └───────┬───────────────┬─────────────────┘
                            │               │
            ┌───────────────▼──────┐ ┌──────▼──────────────┐
            │  Agent runtime       │ │  Scheduler          │
            │  (LangGraph graph:   │ │  (APScheduler,      │
            │   plan→act→verify)   │ │   persistent store) │
            └───────┬──────────────┘ └─────────────────────┘
                    │
        ┌───────────┼───────────────┬──────────────┐
        ▼           ▼               ▼              ▼
  ┌──────────┐ ┌─────────┐ ┌──────────────┐ ┌───────────┐
  │ Gateway  │ │ Memory  │ │ Tool sandbox │ │ Browser   │
  │(LiteLLM: │ │(mem0 +  │ │ (Docker,     │ │(Playwright│
  │ routing, │ │ SQLite  │ │ allowlists,  │ │container, │
  │ fallback,│ │ FTS5 +  │ │ receipts,    │ │ profiles, │
  │ budgets) │ │ md mir.)│ │ approvals)   │ │ takeover) │
  └──────────┘ └─────────┘ └──────────────┘ └───────────┘
```

## Key design rules

1. **Provider logic never touches the agent core.** The gateway exposes one interface (ACP-style neutrality); swapping Groq for Ollama is a config change.
2. **Every consequential action is gated.** LangGraph interrupts pause the graph; the user approves/rejects in the UI; every action writes a signed tool receipt to the audit log.
3. **Memory is user-owned.** mem0 for retrieval; a human-readable `USER.md`/`MEMORY.md` mirror the user can edit; export and delete are first-class flows, not settings-page afterthoughts.
4. **Budgets are enforced, not suggested.** Each task gets token/call/cost caps from the gateway; exhaustion pauses the task and tells the user why.
5. **Tool output is untrusted data.** Retrieved pages, docs, and tool results are never treated as instructions (prompt-injection boundary, see `docs/security.md`).
6. **Honest boundaries.** Like openmuse's VERIFICATION.md: the UI labels what's verified working, what's experimental, and what's a placeholder. No mocked integrations presented as real.

## Product differentiators (why NovaPilot, not the 12 products above)

1. **Audited autonomy with consumer UX** — zeroclaw-grade tool receipts and tiered autonomy behind a web approval surface nobody has built.
2. **Memory you can read and own** — letta-grade architecture (blocks + dreaming) with nanobot-grade human-readable mirrors, local-first, exportable, deletable.
3. **Budgets as a feature** — per-task cost/latency caps with provider fallback routing; the agent tells you what it spent and why.
4. **The web app slot is empty** — every serious contender is CLI/TUI-first. NovaPilot leads with the polished web UI: streaming tool activity, task feed, browser workspace with human takeover.
5. **Honesty as a feature** — verified-vs-planned labeling everywhere; reproducible evals published from day one (nobody else does this).

## Repository tree

```
novapilot/
├── README.md                  # product readme, truthful demo
├── LICENSE                    # Apache-2.0
├── CONTRIBUTING.md
├── SECURITY.md                # vulnerability reporting
├── .gitignore  .env.example   # safe defaults, no secrets
├── docker-compose.yml         # api + worker + browser sandbox
├── pyproject.toml             # uv-managed Python deps
├── apps/web/                  # React + Vite + Tailwind UI
├── services/
│   ├── api/                   # FastAPI: auth, chat, tasks, approvals, audit
│   └── worker/                # scheduler + background job runner
├── packages/
│   ├── agent-core/            # LangGraph graphs: plan → act → verify
│   ├── model-gateway/         # LiteLLM wrapper: routing, fallback, budgets
│   ├── memory/                # mem0 self-hosted + provenance + md mirror
│   ├── tools/                 # sandboxed tool registry + receipts
│   ├── browser/               # Playwright module: local ↔ cloud, profiles
│   ├── scheduler/             # APScheduler jobs, quiet hours, budgets
│   └── security/              # auth, secrets, injection guards, audit
├── tests/{unit,integration,security,evaluations}/
├── research/                  # competitor matrix, evidence, ADRs (this work)
├── docs/                      # architecture, cost, security, roadmap, setup
└── scripts/  .github/workflows/
```

Packages are created as they're implemented (Milestones 2–7) — no empty-package theater; the tree above is the target, `docs/roadmap.md` tracks what's real.
