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
Data (SQLite) lives in the `novapilot-data` volume.

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
# {"ok": true, "service": "novapilot-api", "milestone": 2, "model_default": "ollama/gpt-oss:20b"}

cd services/api && pytest -q                       # API tests (stubbed gateway, no keys)
cd ../../packages/model-gateway && pytest -q       # gateway tests (fallback + budgets)
cd ../../apps/web && npm run build                 # web build
```

## Notes

- `NOVAPILOT_TOKEN` unset = API open (local dev). Set it on any shared network —
  the web UI's Settings page stores it and sends it as a Bearer token.
- `DATABASE_URL` switches to Postgres (`postgresql+asyncpg://…`) for multi-user setups.
- `docker-compose` needs a Docker host; it is validated in CI on every push.
