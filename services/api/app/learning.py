"""Learning singletons: skill store, skills provider for the planner, dreaming."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from novapilot_learning import DreamConsolidator, SkillStore

from .config import settings

log = logging.getLogger("novapilot.learning")

_skill_store: SkillStore | None = None


def skills_dir() -> Path:
    d = Path(settings.workspace_dir) / "skills"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _dreamed_path() -> Path:
    d = Path(settings.workspace_dir)
    d.mkdir(parents=True, exist_ok=True)
    return d / "dreamed.json"


def _load_dreamed() -> set[str]:
    p = _dreamed_path()
    if not p.is_file():
        return set()
    try:
        return set(json.loads(p.read_text()))
    except Exception:  # noqa: BLE001 — corrupt file resets cleanly
        return set()


def _save_dreamed(ids: set[str]) -> None:
    _dreamed_path().write_text(json.dumps(sorted(ids)))


def get_skill_store() -> SkillStore:
    global _skill_store
    if _skill_store is None:
        _skill_store = SkillStore(skills_dir())
    return _skill_store


def skills_provider(goal: str) -> list[dict]:
    """Relevant skills for the planner prompt. Never raises."""
    try:
        return [
            {"name": s.name, "description": s.description}
            for s in get_skill_store().find_relevant(goal)
        ]
    except Exception:
        log.debug("skills lookup failed", exc_info=True)
        return []


async def run_dreaming(limit: int = 20) -> dict:
    """Consolidate recent completed tasks into durable memories. Returns stats."""
    from .agent import get_runner
    from .gateway_dep import get_gateway
    from .memory import get_memory_service

    runner = get_runner()
    tasks = await runner.store.list(limit=limit * 2)
    dreamed = _load_dreamed()
    fresh = [
        t for t in tasks
        if t.get("status") == "completed" and t.get("summary") and t["id"] not in dreamed
    ]
    if not fresh:
        return {"tasks_considered": 0, "facts_stored": 0}

    gateway = get_gateway()
    memory_svc = await get_memory_service()
    consolidator = DreamConsolidator(gateway, memory_svc, settings.memory_namespace)
    stored = await consolidator.consolidate(fresh[:limit])

    _save_dreamed(dreamed | {t["id"] for t in fresh[:limit]})
    return {"tasks_considered": len(fresh[:limit]), "facts_stored": len(stored), "facts": stored}
