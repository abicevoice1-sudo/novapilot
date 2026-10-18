#!/usr/bin/env bash
# Actlet one-line installer.
# Usage: curl -fsSL https://raw.githubusercontent.com/abicevoice1-sudo/actlet/master/install.sh | bash
# Or locally: ./install.sh
#
# What it does:
#   1. Checks for python3.12+, node, npm
#   2. Creates a venv and installs all Actlet packages (editable)
#   3. Builds the web UI
#   4. Writes .env from .env.example (if missing)
#   5. Prints next steps
#
# Nothing is started automatically. No keys required for the default
# local setup (Ollama at http://localhost:11434).

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

echo "==> Actlet installer"
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
echo "==> Installing Actlet packages (editable)"
"$PIP" install -q -e ./packages/model-gateway -e ./packages/agent-core \
  -e ./packages/memory -e ./packages/scheduler -e ./packages/learning \
  -e ./packages/browser -e ./packages/channels -e ./packages/mcp \
  -e ./services/api
echo "    done"

# --- Playwright browsers (optional, needed for the browser workspace) ---
if "$VENV/bin/python" -c "import playwright" 2>/dev/null; then
  echo "==> Installing Playwright Chromium (skip with ACTLET_SKIP_BROWSERS=1)"
  if [ "${ACTLET_SKIP_BROWSERS:-0}" != "1" ]; then
    "$VENV/bin/playwright" install chromium --with-deps 2>/dev/null \
      || "$VENV/bin/playwright" install chromium \
      || echo "    WARNING: Chromium install failed — browser features need it. Re-run: .venv/bin/playwright install chromium"
  fi
fi

# --- Web UI ---
echo "==> Building web UI"
(cd apps/web && npm ci -q && npm run build -s)
echo "    done (apps/web/dist)"

# --- Config ---
if [ ! -f "$REPO_DIR/.env" ]; then
  cp "$REPO_DIR/.env.example" "$REPO_DIR/.env"
  echo "==> Wrote .env from .env.example (edit it to add keys)"
else
  echo "==> .env already exists — leaving it alone"
fi

echo ""
echo "================================================================"
echo "  Actlet installed. Next steps:"
echo ""
echo "  1. (Optional) Start Ollama for free local models:"
echo "       ollama pull gpt-oss:20b && ollama serve"
echo ""
echo "  2. Start the API:"
echo "       .venv/bin/uvicorn app.main:app --app-dir services/api"
echo ""
echo "  3. Open http://localhost:8000 — the web UI is served from the API."
echo ""
echo "  Optional: set a ACTLET_TOKEN in .env to lock the API with"
echo "  bearer auth. Add Telegram / MCP config in .env to connect channels."
echo "================================================================"
