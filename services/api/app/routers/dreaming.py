"""Dreaming endpoints: run consolidation now; make a skill from a task."""

import json

from fastapi import APIRouter, Depends, HTTPException
from novapilot_learning import Skill
from pydantic import BaseModel

from ..auth import require_auth
from ..learning import get_skill_store, run_dreaming

router = APIRouter(tags=["dreaming"])


@router.post("/api/dreaming/run", dependencies=[Depends(require_auth)])
async def run_dreaming_now():
    """Consolidate recent completed tasks into durable memories."""
    try:
        return await run_dreaming()
    except Exception as e:
        raise HTTPException(502, f"dreaming needs a reachable model: {e}") from e


MAKE_SKILL_PROMPT = """Study this completed agent task and write a reusable SKILL for it:
a short playbook the agent can follow next time a similar goal appears.

Return ONLY JSON: {{"name": "kebab-case-name", "description": "one line",
"instructions": "markdown steps", "tools": ["tool names used"]}}.
Instructions must be concrete (which tools, in what order, what to verify).
If the task is too one-off to generalize, return {{"skip": true}}.

GOAL: {goal}
STEPS:
{steps}
"""


class MakeSkillResult(BaseModel):
    name: str | None = None
    skipped: bool = False


@router.post("/api/tasks/{task_id}/make-skill", dependencies=[Depends(require_auth)])
async def make_skill_from_task(task_id: str):
    """Synthesize a reusable skill from a completed task (user-triggered)."""
    from ..agent import get_runner
    from ..gateway_dep import get_gateway

    runner = get_runner()
    state = await runner.get_state(task_id)
    if state is None:
        raise HTTPException(404, "task not found")
    if state.get("status") != "completed":
        raise HTTPException(400, "only completed tasks can become skills")
    steps = state.get("plan") or []
    if not steps:
        raise HTTPException(400, "task has no steps to learn from")

    step_lines = "\n".join(
        f"- {s.get('description')}: {s.get('tool')} {s.get('args')}" for s in steps
    )
    try:
        text = await get_gateway().chat(
            [
                {"role": "system", "content": "You output only JSON."},
                {"role": "user", "content": MAKE_SKILL_PROMPT.format(
                    goal=state.get("goal"), steps=step_lines)},
            ]
        )
        data = json.loads(text.strip().removeprefix("```json").removeprefix("```").removesuffix("```"))
    except Exception as e:
        raise HTTPException(502, f"skill synthesis needs a reachable model: {e}") from e

    if data.get("skip"):
        return {"skipped": True}
    try:
        skill = get_skill_store().save(
            Skill(
                name=str(data["name"]).strip(),
                description=str(data.get("description", "")).strip(),
                instructions=str(data.get("instructions", "")).strip(),
                tools=list(data.get("tools") or []),
                created_from=[task_id],
            )
        )
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(502, f"could not parse synthesized skill: {e}") from e
    return {"skipped": False, "name": skill.name}
