# Setup

## Prerequisites

- Python 3.12+, Node 24+, Docker (for `docker-compose`)
- A model: **Ollama** for the $0 default (`ollama pull gpt-oss:20b && ollama serve`),
  or set `GROQ_API_KEY` / `GEMINI_API_KEY` / `OPENROUTER_API_KEY` for free-tier cloud fallbacks.
  With no model reachable, `/api/chat` answers with a clear error — it never pretends.

## Option A — docker-compose (recommended)

```bash
cp .env.example .env   # no keys required for the Ollama default
docker-compose up --build
# web UI → http://localhost:3000, API → http://localhost:8000
```

The `web` container serves the built React app and proxies `/api/*` to the API.
Data (SQLite) lives in the `actlet-data` volume.

## Option B — local dev

```bash
# API
pip install -e ./packages/model-gateway -e ./services/api
cd services/api && uvicorn app.main:app --reload   # → http://localhost:8000

# Web (new terminal)
cd apps/web && npm install && npm run dev          # → http://localhost:5173 (proxies /api)
```

## Verify

```bash
curl localhost:8000/health
# {"ok": true, "service": "actlet-api", "milestone": 3, "model_default": "ollama/gpt-oss:20b"}

cd services/api && pytest -q                       # API tests (stubbed gateway/runner, no keys)
cd ../../packages/model-gateway && pytest -q       # gateway tests (fallback + budgets)
cd ../agent-core && pytest -q                      # agent-core tests (tools, graph, runner)
cd ../../apps/web && npm run build                 # web build
```

## Tasks (Milestone 3)

`POST /api/tasks {"goal": "..."}` — Actlet plans with LangGraph, calls validated
tools, and streams progress as SSE on `/api/tasks/{id}/events`. Tools that write
or change state need your approval (Approve/Reject in the Tasks UI or via
`POST /api/tasks/{id}/approve`). Cancel/pause/resume via
`/api/tasks/{id}/{cancel,pause,resume}`. Per-task cost/token/time budgets are
enforced — a breach pauses the task with an explanation. Task checkpoints live
in `CHECKPOINT_PATH` (default `./checkpoints.db`); a restart marks orphaned
tasks `paused` so they can resume.

## Notes

- `ACTLET_TOKEN` unset = API open (local dev). Set it on any shared network —
  the web UI's Settings page stores it and sends it as a Bearer token.
- `DATABASE_URL` switches to Postgres (`postgresql+asyncpg://…`) for multi-user setups.
- `docker-compose` needs a Docker host; it is validated in CI on every push.
