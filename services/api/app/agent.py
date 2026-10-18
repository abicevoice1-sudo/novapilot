"""TaskRunner singleton: one per API process, per-task gateways from settings."""

from __future__ import annotations

from novapilot_agent import TaskRunner
from novapilot_gateway import ModelGateway

from .config import settings
from .task_store import SqlTaskStore

_runner: TaskRunner | None = None


def build_runner() -> TaskRunner:
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
        store=SqlTaskStore(),
        checkpoint_path=settings.checkpoint_path,
    )


def get_runner() -> TaskRunner:
    global _runner
    if _runner is None:
        _runner = build_runner()
    return _runner


def override_runner(runner: TaskRunner | None) -> None:
    """Tests: swap the singleton."""
    global _runner
    _runner = runner
