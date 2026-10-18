"""Shared fakes for agent-core tests: scripted gateway + in-memory task store."""

from novapilot_gateway import BudgetExceeded


class ScriptedGateway:
    """Gateway stub: chat() pops queued responses; budgets enforced."""

    def __init__(self, scripts=None, max_cost_usd=999.0, max_tokens=999_999):
        self.scripts = list(scripts or [])
        self.max_cost_usd = max_cost_usd
        self.max_tokens = max_tokens
        self.cost_usd = 0.0
        self.tokens = 0
        self.chat_calls = 0

    async def chat(self, messages, model=None):
        self.chat_calls += 1
        if self.scripts:
            return self.scripts.pop(0)
        return "ok"

    async def chat_stream(self, messages, model=None):
        yield "ok"

    def check_budget(self):
        if self.cost_usd >= self.max_cost_usd:
            raise BudgetExceeded(f"cost budget exceeded (${self.cost_usd} >= ${self.max_cost_usd})")
        if self.tokens >= self.max_tokens:
            raise BudgetExceeded("token budget exceeded")

    def usage(self):
        return {"cost_usd": self.cost_usd, "tokens": self.tokens}


class MemoryTaskStore:
    """In-memory TaskStore for tests."""

    def __init__(self):
        self.tasks = {}
        self._events = {}
        self._seq = 0

    async def create(self, goal, model, thread_id):
        self._seq += 1
        tid = f"t{self._seq}"
        self.tasks[tid] = {
            "id": tid,
            "goal": goal,
            "model": model,
            "thread_id": thread_id,
            "status": "pending",
            "current_step": 0,
            "total_steps": 0,
            "error": None,
            "usage": {},
        }
        self._events[tid] = []
        return tid

    async def update(self, task_id, **fields):
        self.tasks[task_id].update(fields)

    async def get(self, task_id):
        return self.tasks.get(task_id)

    async def list(self, limit=50):
        return list(self.tasks.values())[:limit]

    async def add_event(self, task_id, type, payload):
        self._events[task_id].append({"type": type, **payload})

    async def events(self, task_id, after_id=0):
        return self._events[task_id][after_id:]
