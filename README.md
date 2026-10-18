# ⚡ Actlet — the little actor that does your tasks

**Your personal AI agent: it remembers, plans, executes, and keeps working while you're away — with your approval on everything that matters.**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-v0.8.0-brightgreen.svg)](https://github.com/abicevoice1-sudo/actlet/releases)
[![Tests](https://img.shields.io/badge/tests-190%2B%20green-brightgreen.svg)](#verification)

## One command. Zero to running.

```bash
curl -fsSL https://raw.githubusercontent.com/abicevoice1-sudo/actlet/master/install.sh | bash
```

That's it. It installs everything, generates your secure token, starts the server, and opens your browser to the Actlet UI. No API keys needed — local models by default, $0.

![Actlet driving a real browser](docs/assets/browser-demo.png)

## Why Actlet

Twenty personal-agent projects were researched live before a line of architecture was drawn ([research/competitor-matrix.md](research/competitor-matrix.md)). Nobody clears 8/10. Actlet is built to fill the gaps they all leave:

| What Actlet does | Why it matters |
|---|---|
| **Approval gates on every consequential action** | The agent *cannot* click, write, send, or spend without your explicit approval — enforced in code, not in prompts. Prompt-injection tested. |
| **Memory you can read, edit, and delete** | Local-first, full-text searchable, exportable. It even dreams: nightly consolidation turns your task history into durable knowledge. |
| **Per-task budgets, enforced** | Cost, token, and time caps per task with automatic provider fallback. You'll never wake up to a surprise bill. |
| **A real web UI** | Chat, tasks, schedules, skills, memory, browser screenshots — every serious contender is CLI-first. |
| **Honesty as a feature** | Verified-vs-planned labeling everywhere. We publish what works, what doesn't, and what's untested. |

## What it can do

- 🧠 **Remember** — user-owned memory with redaction, dedup, export/import
- 📅 **Schedule** — "every morning at 8" → recurring agent tasks with missed-run replay, quiet hours, and one-tap pause
- 🌙 **Learn** — nightly dreaming consolidation + reusable skills you can export and share
- 🌐 **Browse** — real Chromium with scoped navigation, 12 approval-gated tools, screenshots at every step
- 📧 **Connect** — Telegram, Gmail (read/send), calendar (CalDAV), and any MCP server
- 👥 **Delegate** — specialist sub-agents (researcher, coder, browser operator, communicator) with restricted toolsets
- 🛡️ **Stay safe** — prompt-injection evals, workspace checkpoints with one-click revert, Docker sandbox for shell

## Quickstart

```bash
# One-line install (Python 3.12+, Node required)
curl -fsSL https://raw.githubusercontent.com/abicevoice1-sudo/actlet/master/install.sh | bash

# Start (Ollama default — $0, no keys)
.venv/bin/uvicorn app.main:app --app-dir services/api
```

Open http://localhost:8000. Set `ACTLET_TOKEN` in `.env` to lock the API. Add `GMAIL_*`, `CALDAV_*`, or `TELEGRAM_BOT_TOKEN` to connect your accounts. Full guide: [docs/setup.md](docs/setup.md).

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Web UI    │────▶│  FastAPI     │────▶│  LangGraph  │
│ React+Tail  │     │  + SSE       │     │ plan→execute│
└─────────────┘     └──────────────┘     │ →summarize │
       │                    │            └─────────────┘
       │            ┌───────┴────────┐          │
       │            │ Channels     │    ┌─────┴──────┐
       └───────────▶│ TG/Gmail/MCP │    │  LiteLLM   │
                    └──────────────┘    │  gateway   │
                                        └────────────┘
```

**Stack:** Python 3.12 + FastAPI · LangGraph · LiteLLM (Ollama default, free-tier fallbacks) · SQLite+FTS5 → Postgres · React 18 + Vite + Tailwind · Playwright. See [docs/architecture.md](docs/architecture.md) and the 10 ADRs in [research/architecture-decisions.md](research/architecture-decisions.md).

## Verification

We don't claim what we can't prove:

- **170+ tests green** across 11 packages + API (`pytest`), ruff clean, web build green
- **Live-verified flows:** scheduler fired real tasks · dreaming stored real facts · MCP served a real task · browser ran a real Chromium flow (5 approvals, 4 screenshots) · checkpoints reverted real files
- **Honestly labeled limits:** Docker sandbox and mem0 backend are code-complete but untested against real Docker/mem0 in CI — marked as such in [docs/roadmap.md](docs/roadmap.md)

## Cost

**$0 by default.** Local Ollama inference, free-tier cloud fallbacks (Groq → Gemini → OpenRouter), local-first everything. See [docs/cost-model.md](docs/cost-model.md) for verified quotas.

## Security

Threat model in [docs/security.md](docs/security.md) · injection evals in [tests/security/](tests/security/) · report vulnerabilities privately per [SECURITY.md](SECURITY.md) — never as public issues.

## Roadmap

Every phase ships as: build → tests → live verify → docs → commit. Current status in [docs/roadmap.md](docs/roadmap.md).

## License

Apache-2.0. See [LICENSE](LICENSE).
