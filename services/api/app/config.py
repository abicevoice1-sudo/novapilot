"""Application settings. All overridable via environment / .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Actlet"
    database_url: str = "sqlite+aiosqlite:///./actlet.db"

    # Model gateway
    model_default: str = "nvidia_nim/meta/llama-3.3-70b-instruct"
    model_fallbacks: str = "groq/llama-3.3-70b-versatile,gemini/gemini-2.5-flash,ollama/gpt-oss:20b"
    ollama_base_url: str = "http://localhost:11434"

    # Per-task budgets (enforced, not suggested)
    task_max_cost_usd: float = 0.50
    task_max_tokens: int = 200_000
    task_max_wallclock_sec: int = 1800

    # Agent task checkpoints (LangGraph checkpointer; SQLite file)
    checkpoint_path: str = "./checkpoints.db"

    # Memory (M4)
    memory_path: str = "./memories.db"
    memory_namespace: str = "default"

    # Browser workspace (M5)
    workspace_dir: str = "./workspace"
    # Comma-separated domains the agent browser may visit. Empty = unrestricted.
    browser_allowed_domains: str = ""

    # Security: if ACTLET_TOKEN is set, /api/* requires Bearer auth.
    # Unset = open (local dev default), with a logged warning.
    actlet_token: str = ""

    # Channels (Phase C): Telegram bot. Unset = channel disabled.
    telegram_bot_token: str = ""
    # Comma-separated Telegram user IDs allowed to use the bot.
    # Empty = NO ONE (deny-by-default; audit fix).
    telegram_allowed_users: str = ""

    # MCP servers (Phase C): JSON map of name -> {command, args}. Unset = none.
    mcp_servers: str = ""

    # Gmail (Phase F): address + Google App Password. Unset = disabled.
    gmail_address: str = ""
    gmail_app_password: str = ""
    # Comma-separated sender addresses allowed to trigger tasks.
    # Empty = NO ONE (deny-by-default; audit fix).
    gmail_allowed_senders: str = ""

    # Slack (Phase I): bot token + app token (Socket Mode). Unset = disabled.
    slack_bot_token: str = ""
    slack_app_token: str = ""
    # Comma-separated Slack user IDs allowed.
    # Empty = NO ONE (deny-by-default; audit fix).
    slack_allowed_users: str = ""

    # Quiet hours (Phase F): HH:MM local time. Schedules don't fire inside
    # the window (run-now still works). Empty = no quiet hours.
    quiet_hours_start: str = ""
    quiet_hours_end: str = ""

    # Calendar (Phase G): CalDAV endpoint + credentials. Unset = disabled.
    # Google: https://apidata.googleusercontent.com/caldav/v2/YOU@gmail.com/events
    # with an App Password (same as Gmail).
    caldav_url: str = ""
    caldav_username: str = ""
    caldav_password: str = ""
    secret_key: str = "change-me"

    log_level: str = "INFO"

    @property
    def fallback_list(self) -> tuple[str, ...]:
        return tuple(m.strip() for m in self.model_fallbacks.split(",") if m.strip())


settings = Settings()
