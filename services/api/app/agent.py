"""TaskRunner singleton: one per API process, per-task gateways from settings."""

from __future__ import annotations

from novapilot_agent import TaskRunner
from novapilot_agent.tools import builtin_registry
from novapilot_gateway import ModelGateway
from novapilot_memory.tools import register_memory_tools

from .config import settings
from .task_store import SqlTaskStore

_runner: TaskRunner | None = None


def build_runner(memory_service) -> TaskRunner:
    registry = builtin_registry()
    register_memory_tools(registry, memory_service, lambda: settings.memory_namespace)

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
