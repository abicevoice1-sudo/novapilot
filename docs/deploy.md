# Deploying Actlet

Three ways, cheapest first.

## 1. Local (free, 2 minutes)

```bash
curl -fsSL https://raw.githubusercontent.com/abicevoice1-sudo/actlet/master/install.sh | bash
.venv/bin/uvicorn app.main:app --app-dir services/api
```

Ollama runs the models locally — $0, no API keys. Open http://localhost:8000.

## 2. Docker Compose (self-hosted server)

```bash
cp full.env.example .env        # fill in ACTLET_TOKEN + any integrations
docker compose up -d --build
```

API on :8000, web UI on :3000. Data persists in the `actlet-data` volume.

## 3. Fly.io (one command, free tier)

```bash
fly launch --no-deploy
fly secrets set ACTLET_TOKEN=your-token
fly deploy
```

`fly.toml` is included. The API serves the web UI, so one machine does it all.
A 1GB volume holds the SQLite database and workspace at `/data`.

## Production checklist

- [ ] `ACTLET_TOKEN` set (locks the API; the web UI prompts for it)
- [ ] `WORKSPACE_DIR` on persistent storage (volume or mounted disk)
- [ ] Back up `/data/actlet.db` nightly — it holds memory, tasks, and schedules
- [ ] `QUIET_HOURS_START` / `QUIET_HOURS_END` set so scheduled tasks don't ping at night
- [ ] `BROWSER_ALLOWED_DOMAINS` set to the sites you actually use
- [ ] Reverse proxy (Caddy/nginx) with HTTPS in front if not using Fly
- [ ] `fly logs` / `docker compose logs` for monitoring; `/api/health` for uptime checks

## What NOT to do

- Don't expose the API without `ACTLET_TOKEN`. Approval gates protect actions,
  but the token protects the whole control plane.
- Don't run the Docker sandbox (`ACTLET_SANDBOX=docker`) on a shared host
  without understanding container escape risks — see docs/security.md.
