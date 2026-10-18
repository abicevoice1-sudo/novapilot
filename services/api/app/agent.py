"""TaskRunner singleton: one per API process, per-task gateways from settings."""

from __future__ import annotations

from pathlib import Path

from actlet_agent import TaskRunner
from actlet_agent.checkpoints import CheckpointManager
from actlet_agent.tools import builtin_registry
from actlet_browser import BrowserSession
from actlet_browser.tools import register_browser_tools
from actlet_gateway import ModelGateway
from actlet_memory.tools import register_memory_tools

from .config import settings
from .learning import skills_provider
from .task_store import SqlTaskStore

_checkpoint_manager: CheckpointManager | None = None


def get_checkpoint_manager() -> CheckpointManager:
    global _checkpoint_manager
    if _checkpoint_manager is None:
        _checkpoint_manager = CheckpointManager(settings.workspace_dir)
    return _checkpoint_manager

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
    # ONE canonical workspace path: settings.workspace_dir. Injected into the
    # tool registry so file tools, checkpoints, browser shots, and skills all
    # operate in the same directory (audit fix).
    registry = builtin_registry(workspace_dir=settings.workspace_dir)
    register_memory_tools(registry, memory_service, lambda: settings.memory_namespace)
    register_browser_tools(registry, get_browser_session)
    if settings.gmail_address and settings.gmail_app_password:
        from actlet_gmail import GmailClient, register_gmail_tools

        def _gmail_factory() -> GmailClient:
            return GmailClient(settings.gmail_address, settings.gmail_app_password)

        register_gmail_tools(registry, _gmail_factory)
    if settings.caldav_url and settings.caldav_username and settings.caldav_password:
        from actlet_calendar import CalendarClient, register_calendar_tools

        def _cal_factory() -> CalendarClient:
            return CalendarClient(
                settings.caldav_url, settings.caldav_username, settings.caldav_password
            )

        register_calendar_tools(registry, _cal_factory)

    def gateway_factory() -> ModelGateway:
        return ModelGateway(
            default_model=settings.model_default,
            fallbacks=settings.fallback_list,
            max_cost_usd=settings.task_max_cost_usd,
            max_tokens=settings.task_max_tokens,
            max_wallclock_sec=settings.task_max_wallclock_sec,
        )

    runner = TaskRunner(
        gateway_factory=gateway_factory,
        registry=registry,
        store=SqlTaskStore(),
        checkpoint_path=settings.checkpoint_path,
        skills_provider=skills_provider,
        checkpoint_manager=get_checkpoint_manager(),
    )
    from actlet_agent import register_delegate_tool

    register_delegate_tool(registry, runner.run_delegate)
    return runner


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
