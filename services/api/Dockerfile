# Build context is the repo root (needs packages/model-gateway too).
FROM python:3.12-slim
WORKDIR /app
COPY packages/model-gateway /tmp/gateway
COPY services/api/pyproject.toml .
RUN pip install --no-cache-dir /tmp/gateway . && rm -rf /tmp/gateway
COPY services/api/app/ app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
