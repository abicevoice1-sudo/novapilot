"""TaskRunner: task lifecycle on top of the agent graph.

States: pending → running → (waiting_approval → running)* → completed
                              ↘ paused (budget / pause request / restart) → running (resume)
                              ↘ failed → running (resume) | cancelled (terminal)

Every state transition and tool action emits an event to a per-task bus
(persisted via the TaskStore, streamed to SSE subscribers). Approval gates use
LangGraph interrupts; resume continues the same thread from its checkpoint.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.errors import GraphInterrupt
from langgraph.types import Command

from .delegate import SPECIALISTS, current_task_id
from .graph import build_graph
from .store import TaskStore
from .tools import ToolRegistry, builtin_registry

# Backwards-compat alias (graph.py used this name before the move).
_current_task_id = current_task_id


def _task_id() -> str | None:
    return current_task_id.get()

log = logging.getLogger("novapilot.runner")


class TaskRunner:
    def __init__(
        self,
        gateway_factory,
        registry: ToolRegistry | None = None,
        checkpointer=None,
        store: TaskStore | None = None,
        checkpoint_path: str = "./checkpoints.db",
        skills_provider=None,
        checkpoint_manager=None,
    ) -> None:
        self.gateway_factory = gateway_factory
        self.registry = registry or builtin_registry()
        self.store = store
        self._skills_provider = skills_provider
        self._checkpoint_manager = checkpoint_manager
        # The default AsyncSqliteSaver needs async setup, so it is created
        # lazily on first use (tests pass an InMemorySaver directly).
        self._checkpointer_cm = None
        self._checkpoint_path = checkpoint_path
        self.checkpointer = checkpointer
        self.graph = build_graph(self.registry, checkpointer, skills_provider, self._checkpoint_manager) if checkpointer else None
        self._queues: dict[str, asyncio.Queue] = {}
        self._tasks: dict[str, asyncio.Task] = {}
        self._controls: dict[str, dict] = {}
        self._seq: dict[str, int] = {}

    async def _ensure_ready(self) -> None:
        if self.graph is None:
            self._checkpointer_cm = AsyncSqliteSaver.from_conn_string(self._checkpoint_path)
            self.checkpointer = await self._checkpointer_cm.__aenter__()
            self.graph = build_graph(self.registry, self.checkpointer, self._skills_provider, self._checkpoint_manager)

    async def aclose(self) -> None:
        if self._checkpointer_cm is not None:
            await self._checkpointer_cm.__aexit__(None, None, None)
            self._checkpointer_cm = None

    # ------------------------------------------------------------ lifecycle

    async def create_task(
        self,
        goal: str,
        model: str | None = None,
        preapproved_tools: list[str] | None = None,
        source: str | None = None,
    ) -> str:
        """Create and drive a task.

        preapproved_tools: tool names that skip approval gates (schedule-granted;
        every skip is audit-logged). source: e.g. "schedule:<id>" for attribution.
        """
        if self.store is None:
            raise RuntimeError("TaskRunner needs a TaskStore")
        thread_id = f"task-{uuid.uuid4().hex[:12]}"
        task_id = await self.store.create(goal, model, thread_id, source=source)
        self._ensure_runtime(task_id)
        self._controls[task_id]["gateway"] = self.gateway_factory()
        self._controls[task_id]["preapproved_tools"] = set(preapproved_tools or [])
        await self.store.update(task_id, status="running")
        self._tasks[task_id] = asyncio.create_task(
            self._drive(task_id, thread_id, {"goal": goal, "model": model})
        )
        return task_id

    def _ensure_runtime(self, task_id: str) -> None:
        self._queues.setdefault(task_id, asyncio.Queue())
        self._controls.setdefault(
            task_id, {"cancel_requested": False, "pause_requested": False, "approvals": {}}
        )

    def _config(self, task_id: str, thread_id: str) -> dict:
        control = self._controls[task_id]
        return {
            "configurable": {
                "thread_id": thread_id,
                "task_id": task_id,
                "emit": self._make_emit(task_id),
                "control": control,
                "gateway": control.get("gateway") or self.gateway_factory(),
            }
        }

    def _make_emit(self, task_id: str):
        async def emit(type: str, payload: dict) -> None:
            self._seq[task_id] = self._seq.get(task_id, 0) + 1
            event = {"seq": self._seq[task_id], "type": type, **payload}
            q = self._queues.get(task_id)
            if q is not None:
                q.put_nowait(event)
            try:
                await self.store.add_event(task_id, type, event)
            except Exception:
                log.exception("task %s: persisting event %s failed", task_id, type)

        return emit

    async def _drive(self, task_id: str, thread_id: str, payload) -> None:
        """Run the graph (initial state or Command) to pause/completion/interrupt."""
        await self._ensure_ready()
        if task_id not in self._seq:
            # after a restart, continue sequence numbers past persisted history
            history = await self.store.events(task_id)
            self._seq[task_id] = max([e.get("seq", 0) for e in history] + [0])
        config = self._config(task_id, thread_id)
        try:
            result = await self.graph.ainvoke(payload, config)
        except GraphInterrupt:  # safety net; 1.2.x surfaces interrupts in the result
            await self.store.update(task_id, status="waiting_approval")
            log.info("task %s waiting for approval", task_id)
            return
        except asyncio.CancelledError:
            await self.store.update(task_id, status="cancelled")
            raise
        except Exception as e:
            log.exception("task %s crashed", task_id)
            await self.store.update(task_id, status="failed", error=f"{type(e).__name__}: {e}")
            return
        finally:
            self._tasks.pop(task_id, None)

        if (result or {}).get("__interrupt__"):
            await self.store.update(task_id, status="waiting_approval")
            log.info("task %s waiting for approval", task_id)
            return

        status = (result or {}).get("status", "completed")
        usage = self._controls[task_id].get("gateway")
        fields: dict = {
            "status": status,
            "current_step": (result or {}).get("step_index", 0),
            "total_steps": len((result or {}).get("plan", [])),
            "usage_json": json.dumps(usage.usage() if usage else {}),
        }
        if (result or {}).get("error"):
            fields["error"] = result["error"]
        if (result or {}).get("summary"):
            fields["summary"] = result["summary"]
        await self.store.update(task_id, **fields)
        log.info("task %s -> %s", task_id, status)

    # ------------------------------------------------------------ controls

    async def approve(self, task_id: str, approved: bool) -> None:
        task = await self.store.get(task_id)
        if not task or task["status"] != "waiting_approval":
            raise ValueError("task is not waiting for approval")
        self._ensure_runtime(task_id)
        await self.store.update(task_id, status="running")
        self._tasks[task_id] = asyncio.create_task(
            self._drive(task_id, task["thread_id"], Command(resume=approved))
        )

    async def cancel(self, task_id: str) -> None:
        task = await self.store.get(task_id)
        if not task:
            raise ValueError("unknown task")
        control = self._controls.get(task_id)
        if control is not None:
            control["cancel_requested"] = True
        running = self._tasks.get(task_id)
        if running is not None:
            running.cancel()
        else:
            # not actively running (e.g. waiting for approval): mark directly
            await self.store.update(task_id, status="cancelled")

    async def pause(self, task_id: str) -> None:
        control = self._controls.get(task_id)
        if control is not None:
            control["pause_requested"] = True
        else:
            await self.store.update(task_id, status="paused", error="paused")

    async def resume(self, task_id: str) -> None:
        task = await self.store.get(task_id)
        if not task or task.get("status") not in ("paused", "failed"):
            raise ValueError("only paused or failed tasks can resume")
        self._ensure_runtime(task_id)
        control = self._controls[task_id]
        control["pause_requested"] = False
        control["cancel_requested"] = False
        if "gateway" not in control:
            control["gateway"] = self.gateway_factory()
        await self.store.update(task_id, status="running", error=None)
        # None payload: continue from the thread's checkpoint
        self._tasks[task_id] = asyncio.create_task(
            self._drive(task_id, task["thread_id"], None)
        )

    async def reconcile(self) -> None:
        """Startup: tasks left running by a dead process become resumable."""
        if self.store is None:
            return
        for t in await self.store.list():
            if t["status"] in ("running", "waiting_approval"):
                await self.store.update(
                    t["id"], status="paused", error="interrupted by restart — resume to continue"
                )
                log.info("task %s reconciled to paused", t["id"])

    # ------------------------------------------------------------ inspection

    def subscribe(self, task_id: str) -> asyncio.Queue:
        return self._queues.setdefault(task_id, asyncio.Queue())

    async def get_state(self, task_id: str) -> dict | None:
        task = await self.store.get(task_id)
        if not task:
            return None
        await self._ensure_ready()
        try:
            snap = await self.graph.aget_state(
                {"configurable": {"thread_id": task["thread_id"]}}
            )
            values = snap.values or {}
        except Exception:  # noqa: BLE001 — checkpoint read is best-effort
            values = {}
        return {**task, "plan": values.get("plan", []), "summary": values.get("summary")}

    async def run_delegate(self, role: str, goal: str) -> str:
        """Run a specialist sub-agent inline; returns its summary.

        The sub-agent shares the parent task's approval queue, budget, and
        event stream. Its toolset is restricted to the role; it cannot
        delegate further.
        """
        task_id = current_task_id.get()
        if task_id is None:
            raise RuntimeError("delegate called outside a task")
        spec = SPECIALISTS[role]
        sub_registry = self.registry.subset(spec["tools"])
        await self._ensure_ready()
        sub_graph = build_graph(
            sub_registry, self.checkpointer, self._skills_provider, self._checkpoint_manager
        )
        sub_thread = f"task-{task_id}-sub-{uuid.uuid4().hex[:8]}"
        config = self._config(task_id, sub_thread)
        emit = self._make_emit(task_id)
        await emit("delegate_started", {"role": role, "goal": goal})
        result = await sub_graph.ainvoke({"goal": goal}, config)
        summary = result.get("summary", "") if isinstance(result, dict) else ""
        await emit("delegate_done", {"role": role, "summary": summary[:500]})
        return summary
