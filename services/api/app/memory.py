"""Memory service singleton (embedded backend; mem0 via MEMORY_BACKEND=mem0)."""

from __future__ import annotations

from novapilot_memory import MemoryService, create_service

from .config import settings

_service: MemoryService | None = None
_initialized = False


async def get_memory_service() -> MemoryService:
    global _service, _initialized
    if _service is None:
        import os

        os.environ.setdefault("MEMORY_PATH", settings.memory_path)
        _service = create_service()
        store = getattr(_service, "store", None)
        if store is not None and hasattr(store, "init"):
            await store.init()
            _initialized = True
    return _service


async def close_memory_service() -> None:
    global _service, _initialized
    if _service is not None and _initialized:
        store = getattr(_service, "store", None)
        if store is not None and hasattr(store, "close"):
            await store.close()
    _service = None
    _initialized = False


def override_memory_service(service: MemoryService | None) -> None:
    global _service, _initialized
    _service = service
    _initialized = service is not None
