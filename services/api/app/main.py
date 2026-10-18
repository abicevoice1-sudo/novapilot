"""NovaPilot API — Milestone 1 skeleton.

Implements exactly what Milestone 1 promises: configuration loading and a
health endpoint. The agent runtime, memory, tools, and scheduler arrive in
Milestones 2-7 (see docs/roadmap.md). Nothing is mocked as working.
"""

from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "NovaPilot"
    database_url: str = "sqlite+aiosqlite:///./novapilot.db"
    model_default: str = "ollama/gpt-oss:20b"
    task_max_cost_usd: float = 0.50
    task_max_tokens: int = 200_000
    task_max_wallclock_sec: int = 1800


settings = Settings()
app = FastAPI(title="NovaPilot API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "service": "novapilot-api",
        "milestone": 1,
        "model_default": settings.model_default,
    }
