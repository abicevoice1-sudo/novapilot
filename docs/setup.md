# Setup

## Milestone 1 (today)

You need: Python 3.12+, `pip`.

```bash
cd services/api
pip install -e ".[test]"
pytest -q                    # 2 tests: config + health
uvicorn app.main:app --reload
curl localhost:8000/health   # {"ok": true, "service": "novapilot-api", "milestone": 1}
```

## Milestone 2 target (not yet)

```bash
cp .env.example .env   # no keys required — Ollama default
docker-compose up      # api + worker + browser sandbox
```

Requires: Docker, and Ollama (`ollama pull gpt-oss:20b`) for the $0 default model.
