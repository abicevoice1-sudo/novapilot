"""Provider-neutral model gateway.

One interface for every model provider (ACP-style neutrality: the agent core
never touches provider-specific code). Backed by LiteLLM; the backend is
injectable so tests run without network or keys.

Backend protocol (what ``backend`` must provide):
  - ``await backend.acompletion(model=..., messages=..., stream=False)``
  - ``backend.stream_chunk_builder(chunks)`` -> response-like with ``.usage``
  - ``backend.completion_cost(completion_response=...)`` -> float USD
"""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any


class GatewayError(Exception):
    """No model on the chain could serve the request."""


class BudgetExceeded(GatewayError):
    """A per-task budget (cost, tokens, or wall-clock) was exceeded."""


log = logging.getLogger("novapilot.gateway")


@dataclass(frozen=True)
class ModelInfo:
    id: str
    label: str
    provider: str
    free: bool


DEFAULT_CATALOG: tuple[ModelInfo, ...] = (
    ModelInfo("ollama/gpt-oss:20b", "GPT-OSS 20B (local Ollama)", "ollama", True),
    ModelInfo("groq/gpt-oss-120b", "GPT-OSS 120B (Groq free tier)", "groq", True),
    ModelInfo("gemini/gemini-2.5-flash", "Gemini 2.5 Flash (AI Studio free tier)", "gemini", True),
    ModelInfo("openrouter/qwen/qwen3-32b:free", "Qwen3 32B (OpenRouter free)", "openrouter", True),
)


def _litellm():
    import litellm

    return litellm


class ModelGateway:
    """Route chat requests across a fallback chain with enforced budgets."""

    def __init__(
        self,
        default_model: str = "ollama/gpt-oss:20b",
        fallbacks: tuple[str, ...] = ("groq/gpt-oss-120b", "gemini/gemini-2.5-flash"),
        max_cost_usd: float = 0.50,
        max_tokens: int = 200_000,
        max_wallclock_sec: int = 1800,
        catalog: tuple[ModelInfo, ...] = DEFAULT_CATALOG,
        backend: Any | None = None,
    ) -> None:
        self.default_model = default_model
        self.fallbacks = fallbacks
        self.max_cost_usd = max_cost_usd
        self.max_tokens = max_tokens
        self.max_wallclock_sec = max_wallclock_sec
        self.catalog = catalog
        self._backend = backend
        self.cost_usd: float = 0.0
        self.tokens: int = 0

    @property
    def backend(self) -> Any:
        if self._backend is None:
            self._backend = _litellm()
        return self._backend

    def list_models(self) -> list[ModelInfo]:
        return list(self.catalog)

    def usage(self) -> dict:
        return {"cost_usd": round(self.cost_usd, 6), "tokens": self.tokens}

    def check_budget(self) -> None:
        """Public budget gate: raises BudgetExceeded before a call that can't be afforded."""
        self._check_budget()

    def _chain(self, model: str | None) -> list[str]:
        chain = [model or self.default_model]
        chain += [m for m in self.fallbacks if m not in chain]
        return chain

    def _check_budget(self) -> None:
        if self.cost_usd >= self.max_cost_usd:
            raise BudgetExceeded(f"cost budget exceeded (${self.cost_usd:.4f} >= ${self.max_cost_usd})")
        if self.tokens >= self.max_tokens:
            raise BudgetExceeded(f"token budget exceeded ({self.tokens} >= {self.max_tokens})")

    def _account(self, response: Any, model: str) -> None:
        usage = getattr(response, "usage", None)
        if usage is not None:
            self.tokens += int(getattr(usage, "total_tokens", 0) or 0)
        try:
            self.cost_usd += float(self.backend.completion_cost(completion_response=response) or 0.0)
        except Exception as e:  # noqa: BLE001 — unknown model pricing must not break accounting
            log.debug("completion_cost unavailable for %s: %s", model, e)

    async def chat(self, messages: list[dict], model: str | None = None) -> str:
        """Non-streaming completion with fallback."""
        errors: list[str] = []
        for m in self._chain(model):
            self._check_budget()
            start = time.monotonic()
            try:
                resp = await self.backend.acompletion(model=m, messages=messages, stream=False)
                text = (resp.choices[0].message.content or "").strip()
                if time.monotonic() - start > self.max_wallclock_sec:
                    raise BudgetExceeded("wall-clock budget exceeded")
                self._account(resp, m)
                return text
            except BudgetExceeded:
                raise
            except Exception as e:  # noqa: BLE001 — try next provider
                errors.append(f"{m}: {type(e).__name__}: {e}")
        raise GatewayError("no model reachable (" + "; ".join(errors) + ")")

    async def chat_stream(self, messages: list[dict], model: str | None = None) -> AsyncIterator[str]:
        """Streaming completion with fallback. Yields text deltas."""
        errors: list[str] = []
        for m in self._chain(model):
            self._check_budget()
            start = time.monotonic()
            try:
                chunks: list[Any] = []
                stream = await self.backend.acompletion(model=m, messages=messages, stream=True)
                async for chunk in stream:
                    delta = ""
                    try:
                        delta = chunk.choices[0].delta.content or ""
                    except (AttributeError, IndexError):
                        delta = ""
                    if delta:
                        chunks.append(chunk)
                        yield delta
                if time.monotonic() - start > self.max_wallclock_sec:
                    raise BudgetExceeded("wall-clock budget exceeded")
                built = self.backend.stream_chunk_builder(chunks)
                self._account(built, m)
                return
            except BudgetExceeded:
                raise
            except Exception as e:  # noqa: BLE001 — try next provider
                errors.append(f"{m}: {type(e).__name__}: {e}")
        raise GatewayError("no model reachable (" + "; ".join(errors) + ")")
