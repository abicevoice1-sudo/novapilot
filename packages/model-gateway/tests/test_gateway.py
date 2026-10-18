"""Gateway tests run against a fake backend — no network, no keys, no litellm."""

from types import SimpleNamespace

import pytest

from novapilot_gateway import BudgetExceeded, GatewayError, ModelGateway


class FakeChunk:
    def __init__(self, text):
        self.choices = [SimpleNamespace(delta=SimpleNamespace(content=text))]


class FakeResponse:
    def __init__(self, text, prompt_tokens=10, completion_tokens=5):
        self.choices = [SimpleNamespace(message=SimpleNamespace(content=text))]
        self.usage = SimpleNamespace(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )


class FakeBackend:
    """Programmable failures: fail_models maps model -> exception to raise."""

    def __init__(self, fail_models=None, stream_text="hello world", cost=0.001):
        self.fail_models = fail_models or {}
        self.stream_text = stream_text
        self.cost = cost
        self.calls = []

    async def acompletion(self, model, messages, stream=False):
        self.calls.append(model)
        if model in self.fail_models:
            raise self.fail_models[model]
        if stream:
            async def gen():
                for word in self.stream_text.split(" "):
                    yield FakeChunk(word + " ")

            return gen()
        return FakeResponse(self.stream_text)

    def stream_chunk_builder(self, chunks):
        text = "".join(c.choices[0].delta.content for c in chunks)
        return FakeResponse(text)

    def completion_cost(self, completion_response):
        return self.cost


def make_gateway(**kw):
    kw.setdefault("backend", FakeBackend())
    return ModelGateway(**kw)


async def test_chat_uses_default_model():
    gw = make_gateway()
    assert await gw.chat([{"role": "user", "content": "hi"}]) == "hello world"
    assert gw.backend.calls == ["ollama/gpt-oss:20b"]


async def test_chat_falls_back_on_failure():
    backend = FakeBackend(fail_models={"ollama/gpt-oss:20b": ConnectionError("down")})
    gw = make_gateway(backend=backend)
    assert await gw.chat([{"role": "user", "content": "hi"}]) == "hello world"
    assert backend.calls == ["ollama/gpt-oss:20b", "groq/gpt-oss-120b"]


async def test_chat_all_fail_raises_gateway_error():
    backend = FakeBackend(
        fail_models={
            "ollama/gpt-oss:20b": ConnectionError("down"),
            "groq/gpt-oss-120b": ConnectionError("down"),
            "gemini/gemini-2.5-flash": ConnectionError("down"),
        }
    )
    gw = make_gateway(backend=backend)
    with pytest.raises(GatewayError, match="no model reachable"):
        await gw.chat([{"role": "user", "content": "hi"}])


async def test_chat_stream_yields_deltas_and_accounts_cost():
    gw = make_gateway()
    parts = [p async for p in gw.chat_stream([{"role": "user", "content": "hi"}])]
    assert "".join(parts).strip() == "hello world"
    assert gw.usage()["tokens"] == 15
    assert gw.usage()["cost_usd"] == pytest.approx(0.001)


async def test_budget_exceeded_stops_before_call():
    backend = FakeBackend()
    gw = make_gateway(backend=backend, max_cost_usd=0.0)
    with pytest.raises(BudgetExceeded):
        await gw.chat([{"role": "user", "content": "hi"}])
    assert backend.calls == []


async def test_token_budget_accumulates():
    backend = FakeBackend()
    gw = make_gateway(backend=backend, max_tokens=15)
    await gw.chat([{"role": "user", "content": "hi"}])  # 15 tokens, at the cap
    with pytest.raises(BudgetExceeded):
        await gw.chat([{"role": "user", "content": "hi"}])  # 15 >= 15 → refused before calling


def test_list_models():
    gw = make_gateway()
    models = gw.list_models()
    assert models[0].id == "ollama/gpt-oss:20b"
    assert all(m.free for m in models)
