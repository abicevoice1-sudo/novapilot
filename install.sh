#!/usr/bin/env bash
# Actlet one-click installer.
# Usage: curl -fsSL https://raw.githubusercontent.com/hydope/actlet/master/install.sh | bash
# Or locally: ./install.sh [--no-start]
#
# One command does everything:
#   1. Checks prerequisites (python3.12+, node, npm)
#   2. Creates venv, installs all Actlet packages
#   3. Installs Playwright Chromium for the browser workspace
#   4. Builds the web UI
#   5. Writes .env with a secure auto-generated ACTLET_TOKEN
#   6. Starts the API and opens your browser to the Actlet UI
#
# No API keys needed — local Ollama models are the default ($0).

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

START=1
for arg in "$@"; do
  [ "$arg" = "--no-start" ] && START=0
done

echo "==> Actlet one-click installer"
echo ""

# --- Prerequisites ---
need() {
  command -v "$1" >/dev/null 2>&1 || { echo "MISSING: $1 — please install it first."; MISSING=1; }
}
MISSING=0
need python3; need node; need npm
python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" \
  || { echo "MISSING: python 3.12+ (found $(python3 --version 2>&1))"; MISSING=1; }
if [ "$MISSING" = "1" ]; then
  echo ""; echo "Install the missing prerequisites and re-run."; exit 1
fi
echo "    python3 $(python3 --version | cut -d' ' -f2), node $(node --version), npm $(npm --version)"

# --- Venv ---
VENV="$REPO_DIR/.venv"
if [ ! -d "$VENV" ]; then
  echo "==> Creating venv at .venv"
  python3 -m venv "$VENV"
fi
PIP="$VENV/bin/pip"
"$PIP" install -q --upgrade pip

# --- Python packages ---
# NOTE: no --no-deps. Every package declares its dependencies in pyproject.toml;
# pip resolves them. If this fails, the install fails loudly — a half-installed
# Actlet that crashes on startup is worse than no install.
echo "==> Installing Actlet packages (this takes 2-5 minutes, please wait...)"
"$PIP" install -e ./packages/model-gateway -e ./packages/agent-core \
  -e ./packages/memory -e ./packages/scheduler -e ./packages/learning \
  -e ./packages/browser -e ./packages/channels -e ./packages/mcp \
  -e ./packages/gmail -e ./packages/calendar -e ./services/api
echo "    done"

# --- Playwright Chromium ---
if [ "${ACTLET_SKIP_BROWSERS:-0}" != "1" ]; then
  echo "==> Installing Playwright Chromium (~150MB download, please wait...)"
  "$VENV/bin/playwright" install chromium 2>/dev/null \
    || echo "    WARNING: Chromium install failed — browser features need it."
fi

# --- Web UI ---
echo "==> Building web UI (npm install, takes 1-2 minutes...)"
(cd apps/web && npm ci -q && npm run build -s)
echo "    done"

# --- Config with auto-generated token ---
ENV_FILE="$REPO_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
  cp "$REPO_DIR/.env.example" "$ENV_FILE"
fi
if ! grep -q "^ACTLET_TOKEN=.\+" "$ENV_FILE" 2>/dev/null; then
  TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
  # Replace empty/commented ACTLET_TOKEN line, or append.
  if grep -q "^#\?ACTLET_TOKEN=" "$ENV_FILE"; then
    sed -i.bak "s|^#\?ACTLET_TOKEN=.*|ACTLET_TOKEN=$TOKEN|" "$ENV_FILE" && rm -f "$ENV_FILE.bak"
  else
    echo "ACTLET_TOKEN=$TOKEN" >> "$ENV_FILE"
  fi
  echo "==> Generated a secure ACTLET_TOKEN in .env"
fi
TOKEN="$(grep "^ACTLET_TOKEN=" "$ENV_FILE" | cut -d= -f2-)"

if [ "$START" = "0" ]; then
  echo ""
  echo "Installed (not started — you passed --no-start)."
  echo "Start with: .venv/bin/uvicorn app.main:app --app-dir services/api"
  exit 0
fi

# --- Start ---
echo "==> Starting Actlet"
PID_FILE="$REPO_DIR/.actlet.pid"
if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "    already running (pid $(cat "$PID_FILE"))"
else
  nohup "$VENV/bin/uvicorn" app.main:app --app-dir services/api \
    --host 127.0.0.1 --port 8000 > "$REPO_DIR/.actlet.log" 2>&1 &
  echo $! > "$PID_FILE"
  # Wait for health (max ~20s).
  for _ in $(seq 1 40); do
    if curl -fsS -m 2 http://127.0.0.1:8000/health >/dev/null 2>&1; then
      break
    fi
    sleep 0.5
  done
fi

URL="http://localhost:8000"
if curl -fsS -m 2 http://127.0.0.1:8000/health >/dev/null 2>&1; then
  echo ""
  echo "================================================================"
  echo "  ⚡ Actlet is running!"
  echo ""
  echo "  Open:  $URL"
  echo "  Token: $TOKEN"
  echo "         (the web UI will ask for this once)"
  echo ""
  echo "  Logs:  tail -f .actlet.log"
  echo "  Stop:  kill \$(cat .actlet.pid)"
  echo "================================================================"
  # Open the browser (best effort, never fails the install).
  if command -v xdg-open >/dev/null 2>&1; then
    (xdg-open "$URL" >/dev/null 2>&1 &)
  elif command -v open >/dev/null 2>&1; then
    (open "$URL" >/dev/null 2>&1 &)
  fi
else
  echo ""
  echo "Actlet installed but the API did not become healthy."
  echo "Check .actlet.log, then start manually:"
  echo "  .venv/bin/uvicorn app.main:app --app-dir services/api"
  exit 1
fi
