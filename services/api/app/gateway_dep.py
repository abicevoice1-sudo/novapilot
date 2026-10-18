"""Gateway singleton wired from settings (overridable in tests)."""

from novapilot_gateway import ModelGateway

from .config import settings

_gateway: ModelGateway | None = None


def get_gateway() -> ModelGateway:
    global _gateway
    if _gateway is None:
        _gateway = ModelGateway(
            default_model=settings.model_default,
            fallbacks=settings.fallback_list,
            max_cost_usd=settings.task_max_cost_usd,
            max_tokens=settings.task_max_tokens,
            max_wallclock_sec=settings.task_max_wallclock_sec,
        )
    return _gateway


def override_gateway(gw: ModelGateway | None) -> None:
    """Tests inject a stub; pass None to restore."""
    global _gateway
    _gateway = gw
