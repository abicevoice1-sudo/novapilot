"""LangGraph plan → execute → verify agent loop.

Nodes communicate through typed state; every meaningful transition emits an
event through the ``emit`` callable in config["configurable"]. The per-task
model gateway lives at config["configurable"]["gateway"] (one instance per
task, so budgets are per-task). Approval gates use LangGraph's native
``interrupt()``: the graph pauses and resumes with ``Command(resume=<bool>)``.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
from novapilot_gateway import BudgetExceeded

from .tools import ToolRegistry

log = logging.getLogger("novapilot.graph")

MAX_PLAN_STEPS = 8
MAX_ATTEMPTS = 3
RETRY_BACKOFF = (1, 2, 4)

PLANNER_PROMPT = """You are NovaPilot's planner. Break the goal into concrete steps using ONLY the tools below.
Return ONLY a JSON array. Each step: {{"description": "...", "tool": "<name>", "args": {{...}}}}.
Rules:
- 3 to {max_steps} steps. Args must match each tool's JSON schema.
- Prefer read-only tools; use write_file only to produce a deliverable the goal asks for.
- Verify as you go (e.g. read back a file you wrote).
- Never invent tool names or args.

TOOLS:
{tools}

GOAL: {goal}"""

SUMMARY_PROMPT = """Summarize what was accomplished for the user's goal. Be concrete (files written, facts found).
3-6 sentences, no fluff.

GOAL: {goal}

STEPS:
{steps}"""


class AgentState(TypedDict, total=False):
    goal: str
    model: str | None
    plan: list[dict]
    step_index: int
    status: str
    error: str | None
    summary: str | None


def _cfg(config: RunnableConfig) -> dict:
    return config.get("configurable", {})


async def _emit(config: RunnableConfig, type: str, payload: dict | None = None) -> None:
    emit = _cfg(config).get("emit")
    if emit is not None:
        await emit(type, payload or {})


def _parse_plan(text: str) -> list[dict]:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    data = json.loads(text)
    if not isinstance(data, list):
        raise TypeError("plan must be a JSON array")
    return data


def _validate_plan(plan: list[dict], registry: ToolRegistry) -> list[dict]:
    if not (1 <= len(plan) <= MAX_PLAN_STEPS):
        raise ValueError(f"plan must have 1-{MAX_PLAN_STEPS} steps, got {len(plan)}")
    steps = []
    for i, raw in enumerate(plan):
        if not isinstance(raw, dict) or "tool" not in raw:
            raise ValueError(f"step {i}: must have 'tool'")
        registry.validate(raw["tool"], raw.get("args") or {})
        steps.append(
            {
                "id": str(uuid.uuid4())[:8],
                "description": str(raw.get("description", ""))[:200],
                "tool": raw["tool"],
                "args": raw.get("args") or {},
                "status": "pending",
                "result": None,
                "attempts": 0,
            }
        )
    return steps


def _plan_node(registry: ToolRegistry) -> Any:
    async def plan(state: AgentState, config: RunnableConfig) -> dict:
        await _emit(config, "task_started", {"goal": state["goal"]})
        gateway = _cfg(config)["gateway"]
        model = state.get("model")
        specs = json.dumps(registry.specs())
        prompt = PLANNER_PROMPT.format(max_steps=MAX_PLAN_STEPS, tools=specs, goal=state["goal"])
        last_err = ""
        for attempt in range(2):
            try:
                text = await gateway.chat(
                    [
                        {"role": "system", "content": "You output only JSON."},
                        {
                            "role": "user",
                            "content": prompt
                            + (
                                f"\n\nPrevious attempt failed: {last_err}. Fix it."
                                if last_err
                                else ""
                            ),
                        },
                    ],
                    model=model,
                )
                steps = _validate_plan(_parse_plan(text), registry)
                await _emit(config, "plan_created", {"steps": steps})
                return {"plan": steps, "step_index": 0, "status": "running"}
            except Exception as e:  # noqa: BLE001 — planning may fail; we retry once
                last_err = str(e)
                log.warning("planning attempt %d failed: %s", attempt, e)
        return {"status": "failed", "error": f"planning failed: {last_err}"}

    return plan


def _execute_node(registry: ToolRegistry) -> Any:
    async def execute(state: AgentState, config: RunnableConfig) -> dict:
        cfg = _cfg(config)
        control = cfg.get("control", {})
        if control.get("cancel_requested"):
            await _emit(config, "task_cancelled", {"reason": "cancel requested"})
            return {"status": "cancelled"}
        if control.get("pause_requested"):
            await _emit(config, "task_paused", {"reason": "pause requested"})
            return {"status": "paused"}

        idx = state["step_index"]
        step = state["plan"][idx]
        tool = registry.get(step["tool"])
        await _emit(config, "step_started", {"step": step})

        gateway = cfg["gateway"]
        try:
            gateway.check_budget()
        except BudgetExceeded as e:
            await _emit(config, "budget_exceeded", {"message": str(e), "usage": gateway.usage()})
            return {"status": "paused", "error": f"Budget exceeded: {e}"}

        if tool.requires_approval and step["id"] not in cfg.get("approvals", {}):
            # On resume the node re-executes: don't re-emit the request event.
            seen = control.setdefault("interrupts_emitted", set())
            if step["id"] not in seen:
                await _emit(config, "approval_required", {"step": step})
                seen.add(step["id"])
            decision = interrupt({"step": step})  # first call pauses; resume re-executes and returns the value
            approved = bool(decision is True or (isinstance(decision, dict) and decision.get("approved")))
            await _emit(config, "approval_decided", {"step_id": step["id"], "approved": approved})
            cfg.setdefault("approvals", {})[step["id"]] = approved
            if not approved:
                step = {**step, "status": "skipped", "result": "rejected by user"}
                plan = [s if s["id"] != step["id"] else step for s in state["plan"]]
                return {"plan": plan, "step_index": idx + 1}

        result = None
        receipt: dict = {}
        for attempt in range(1, MAX_ATTEMPTS + 1):
            step = {**step, "status": "running", "attempts": attempt}
            await _emit(config, "tool_called", {"step": step, "attempt": attempt})
            result, receipt = await registry.call(step["tool"], step["args"])
            await _emit(
                config, "tool_result", {"step_id": step["id"], "ok": result.ok, "receipt": receipt}
            )
            if result.ok:
                break
            if attempt < MAX_ATTEMPTS:
                await asyncio.sleep(RETRY_BACKOFF[attempt - 1])
        await _emit(
            config, "step_verified", {"step_id": step["id"], "verification": result.verification}
        )

        status = "done" if result.ok else "failed"
        step = {**step, "status": status, "result": result.output[:2000]}
        plan = [s if s["id"] != step["id"] else step for s in state["plan"]]
        return {"plan": plan, "step_index": idx + 1}

    return execute


def _summarize_node() -> Any:
    async def summarize(state: AgentState, config: RunnableConfig) -> dict:
        gateway = _cfg(config)["gateway"]
        steps_txt = "\n".join(
            f"- [{s['status']}] {s['description']}: {(s.get('result') or '')[:300]}"
            for s in state["plan"]
        )
        try:
            summary = await gateway.chat(
                [
                    {
                        "role": "user",
                        "content": SUMMARY_PROMPT.format(goal=state["goal"], steps=steps_txt),
                    }
                ],
                model=state.get("model"),
            )
        except Exception as e:  # noqa: BLE001 — summary is nice-to-have
            done = sum(1 for s in state["plan"] if s["status"] == "done")
            summary = f"Completed {done}/{len(state['plan'])} steps. ({e})"
        await _emit(config, "task_completed", {"summary": summary, "usage": gateway.usage()})
        return {"status": "completed", "summary": summary}

    return summarize


def _route(state: AgentState) -> str:
    if state.get("status") in ("cancelled", "paused", "failed"):
        return END
    if state["step_index"] >= len(state["plan"]):
        return "summarize"
    return "execute"


def build_graph(registry: ToolRegistry, checkpointer=None):
    """Build the agent graph. checkpointer injectable (InMemorySaver in tests)."""
    builder = StateGraph(AgentState)
    builder.add_node("plan", _plan_node(registry))
    builder.add_node("execute", _execute_node(registry))
    builder.add_node("summarize", _summarize_node())
    builder.add_edge(START, "plan")
    builder.add_conditional_edges("plan", lambda s: END if s.get("status") == "failed" else "execute")
    builder.add_conditional_edges("execute", _route)
    builder.add_edge("summarize", END)
    return builder.compile(checkpointer=checkpointer)
