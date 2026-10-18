# Build context is the repo root (needs packages/*).
FROM python:3.12-slim
WORKDIR /app
COPY packages/model-gateway /tmp/gateway
COPY packages/agent-core /tmp/agent-core
COPY packages/memory /tmp/memory
COPY packages/browser /tmp/browser
COPY services/api/pyproject.toml .
RUN pip install --no-cache-dir /tmp/gateway /tmp/agent-core /tmp/memory /tmp/browser . \
    && playwright install chromium \
    && rm -rf /tmp/gateway /tmp/agent-core /tmp/memory /tmp/browser
COPY services/api/app/ app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
