"""Shared stub gateway for API tests (no network, no keys)."""

from types import SimpleNamespace

from novapilot_gateway import ModelGateway


class StubChunk:
    def __init__(self, text):
        self.choices = [SimpleNamespace(delta=SimpleNamespace(content=text))]


class StubBackend:
    def __init__(self, text="Hello from Nova.", fail=False):
        self.text = text
        self.fail = fail
        self.calls = []

    async def acompletion(self, model, messages, stream=False):
        self.calls.append(model)
        if self.fail:
            raise ConnectionError("model unreachable")

        if stream:

            async def gen():
                for word in self.text.split(" "):
                    yield StubChunk(word + " ")

            return gen()
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.text))],
            usage=SimpleNamespace(prompt_tokens=5, completion_tokens=5, total_tokens=10),
        )

    def stream_chunk_builder(self, chunks):
        text = "".join(c.choices[0].delta.content for c in chunks)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=text))],
            usage=SimpleNamespace(prompt_tokens=5, completion_tokens=5, total_tokens=10),
        )

    def completion_cost(self, completion_response):
        return 0.0


def stub_gateway(**kw):
    kw.setdefault("backend", StubBackend())
    kw.setdefault("fallbacks", ())
    return ModelGateway(default_model="test/echo", **kw)
