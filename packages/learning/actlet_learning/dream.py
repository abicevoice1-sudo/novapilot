"""Dreaming: nightly consolidation of recent work into durable memory.

Reads recently completed tasks (goal + summary), asks the model for durable
learnings about the user (preferences, facts, project context), and stores
them via the memory service — where redaction, dedup, and user ownership
already apply. Nothing is written silently: every fact carries
source="dreaming".
"""

from __future__ import annotations

import json
import logging

log = logging.getLogger("actlet.dreaming")

DREAM_PROMPT = """You review what an AI agent did recently and extract DURABLE learnings
about the user: preferences, recurring projects, facts that will still matter
in a month. Ignore one-off task details.

Return ONLY a JSON array of {{"content": "...", "tags": [...]}}. Empty array if
nothing durable. 3-10 items max. Be concrete: "Syed prefers morning meetings"
not "user likes meetings".

RECENT WORK:
{work}
"""

SUGGEST_PROMPT = """You review an AI agent's recent task history and spot RECURRING patterns
the user would benefit from automating on a schedule. Examples: "check flights
every Friday", "morning news briefing", "weekly inbox triage".

Return ONLY a JSON array of {{"name": "...", "goal": "...", "cadence": "..."}}
where cadence is plain English like "every morning at 8am" or "every Friday at 6pm".
Empty array if no clear recurring pattern. 3 max. Only suggest when the pattern
is strong (same kind of task 2+ times). Do NOT suggest one-off tasks.

RECENT TASKS:
{work}
"""


class DreamConsolidator:
    def __init__(self, gateway, memory_service, namespace: str = "default") -> None:
        self.gateway = gateway
        self.memory = memory_service
        self.namespace = namespace

    async def consolidate(self, tasks: list[dict]) -> list[dict]:
        """tasks: [{goal, summary}]. Returns the facts that were stored."""
        work = [
            f"- Goal: {t.get('goal')}\n  Result: {(t.get('summary') or '')[:500]}"
            for t in tasks
            if t.get("summary")
        ]
        if not work:
            return []
        text = await self.gateway.chat(
            [
                {"role": "system", "content": "You output only JSON."},
                {"role": "user", "content": DREAM_PROMPT.format(work="\n".join(work[:20]))},
            ]
        )
        try:
            items = json.loads(text.strip().removeprefix("```json").removeprefix("```").removesuffix("```"))
            assert isinstance(items, list)
        except Exception as e:  # noqa: BLE001 — a bad dream is dropped, never stored half-parsed
            log.warning("dreaming: could not parse model output: %s", e)
            return []
        stored = []
        for item in items:
            if not isinstance(item, dict) or not item.get("content"):
                continue
            try:
                result = await self.memory.remember(
                    self.namespace,
                    str(item["content"])[:2000],
                    tags=list(item.get("tags") or []),
                    source="dreaming",
                )
                mem = result.get("memory", {}) if isinstance(result, dict) else result
                mem_id = mem.get("id") if isinstance(mem, dict) else getattr(mem, "id", None)
                stored.append({"id": mem_id, "content": str(item["content"])[:2000]})
            except Exception as e:  # noqa: BLE001 — redaction refusals etc. are fine
                log.info("dreaming: skipped a fact (%s)", e)
        log.info("dreaming: stored %d facts from %d tasks", len(stored), len(work))
        return stored

    async def suggest_schedules(self, tasks: list[dict]) -> list[dict]:
        """Spot recurring task patterns and propose schedules for user approval.

        Returns proposals; nothing is created. The user approves via the API.
        """
        goals = [t.get("goal", "") for t in tasks if t.get("goal")]
        if not goals:
            return []
        text = await self.gateway.chat(
            [
                {"role": "system", "content": "You output only JSON."},
                {"role": "user", "content": SUGGEST_PROMPT.format(work="\n".join(goals[:20]))},
            ]
        )
        try:
            items = json.loads(text.strip().removeprefix("```json").removeprefix("```").removesuffix("```"))
            assert isinstance(items, list)
        except Exception as e:  # noqa: BLE001 — a bad dream is dropped
            log.warning("dreaming: could not parse schedule suggestions: %s", e)
            return []
        proposals = []
        for item in items:
            if not isinstance(item, dict) or not item.get("goal") or not item.get("cadence"):
                continue
            proposals.append({
                "name": str(item.get("name") or item["goal"])[:120],
                "goal": str(item["goal"])[:2000],
                "cadence": str(item["cadence"])[:200],
                "source": "dreaming",
            })
        log.info("dreaming: proposed %d schedules", len(proposals))
        return proposals
