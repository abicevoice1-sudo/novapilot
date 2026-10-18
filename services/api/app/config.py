"""Application settings. All overridable via environment / .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "NovaPilot"
    database_url: str = "sqlite+aiosqlite:///./novapilot.db"

    # Model gateway
    model_default: str = "ollama/gpt-oss:20b"
    model_fallbacks: str = "groq/gpt-oss-120b,gemini/gemini-2.5-flash"
    ollama_base_url: str = "http://localhost:11434"

    # Per-task budgets (enforced, not suggested)
    task_max_cost_usd: float = 0.50
    task_max_tokens: int = 200_000
    task_max_wallclock_sec: int = 1800

    # Security: if NOVAPILOT_TOKEN is set, /api/* requires Bearer auth.
    # Unset = open (local dev default), with a logged warning.
    novapilot_token: str = ""
    secret_key: str = "change-me"

    log_level: str = "INFO"

    @property
    def fallback_list(self) -> tuple[str, ...]:
        return tuple(m.strip() for m in self.model_fallbacks.split(",") if m.strip())


settings = Settings()
