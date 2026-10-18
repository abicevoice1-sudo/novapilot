"""Scripted gateway stub for API tests (mirrors agent-core's test fake)."""

from novapilot_gateway import BudgetExceeded


class ScriptedGateway:
    def __init__(self, scripts=None, max_cost_usd=999.0, max_tokens=999_999):
        self.scripts = list(scripts or [])
        self.max_cost_usd = max_cost_usd
        self.max_tokens = max_tokens
        self.cost_usd = 0.0
        self.tokens = 0

    async def chat(self, messages, model=None):
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
