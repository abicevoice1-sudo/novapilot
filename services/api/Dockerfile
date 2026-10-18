# Build context is the repo root (needs packages/* and apps/web).
# Stage 1: build the web UI.
FROM node:20-slim AS web
WORKDIR /web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci -q
COPY apps/web ./
RUN npm run build

# Stage 2: Python API + built UI.
FROM python:3.12-slim
WORKDIR /app
COPY packages/model-gateway /tmp/gateway
COPY packages/agent-core /tmp/agent-core
COPY packages/memory /tmp/memory
COPY packages/browser /tmp/browser
COPY packages/scheduler /tmp/scheduler
COPY packages/learning /tmp/learning
COPY packages/channels /tmp/channels
COPY packages/mcp /tmp/mcp
COPY packages/gmail /tmp/gmail
COPY packages/calendar /tmp/calendar
COPY services/api/pyproject.toml .
RUN pip install --no-cache-dir /tmp/gateway /tmp/agent-core /tmp/memory /tmp/browser \
    /tmp/scheduler /tmp/learning /tmp/channels /tmp/mcp /tmp/gmail /tmp/calendar . \
    && playwright install chromium \
    && rm -rf /tmp/gateway /tmp/agent-core /tmp/memory /tmp/browser /tmp/scheduler \
       /tmp/learning /tmp/channels /tmp/mcp /tmp/gmail /tmp/calendar
COPY services/api/app/ app/
# Web UI built in stage 1; the API serves it from / (see app/main.py).
COPY --from=web /web/dist /app/static/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
