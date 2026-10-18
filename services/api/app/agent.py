"""TaskRunner singleton: one per API process, per-task gateways from settings."""

from __future__ import annotations

from pathlib import Path

from novapilot_agent import TaskRunner
from novapilot_agent.tools import builtin_registry
from novapilot_browser import BrowserSession
from novapilot_browser.tools import register_browser_tools
from novapilot_gateway import ModelGateway
from novapilot_memory.tools import register_memory_tools

from .config import settings
from .learning import skills_provider
from .task_store import SqlTaskStore

_runner: TaskRunner | None = None
_browser: BrowserSession | None = None


def shots_dir() -> Path:
    d = Path(settings.workspace_dir) / "browser-shots"
    d.mkdir(parents=True, exist_ok=True)
    return d


async def get_browser_session() -> BrowserSession:
    """Lazy singleton: Chromium starts on first browser tool use, not at boot."""
    global _browser
    if _browser is None:
        domains = [d.strip() for d in settings.browser_allowed_domains.split(",") if d.strip()]
        _browser = BrowserSession(shots_dir=shots_dir(), allowed_domains=domains)
        await _browser.start()
    return _browser


async def close_browser_session() -> None:
    global _browser
    if _browser is not None:
        await _browser.close()
        _browser = None


def build_runner(memory_service) -> TaskRunner:
    registry = builtin_registry()
    register_memory_tools(registry, memory_service, lambda: settings.memory_namespace)
    register_browser_tools(registry, get_browser_session)

    def gateway_factory() -> ModelGateway:
        return ModelGateway(
            default_model=settings.model_default,
            fallbacks=settings.fallback_list,
            max_cost_usd=settings.task_max_cost_usd,
            max_tokens=settings.task_max_tokens,
            max_wallclock_sec=settings.task_max_wallclock_sec,
        )

    return TaskRunner(
        gateway_factory=gateway_factory,
        registry=registry,
        store=SqlTaskStore(),
        checkpoint_path=settings.checkpoint_path,
        skills_provider=skills_provider,
    )


def get_runner() -> TaskRunner:
    if _runner is None:
        raise RuntimeError("TaskRunner not initialized (lifespan builds it)")
    return _runner


def get_runner_or_none() -> TaskRunner | None:
    return _runner


def override_runner(runner: TaskRunner | None) -> None:
    """Tests: swap the singleton."""
    global _runner
    _runner = runner
