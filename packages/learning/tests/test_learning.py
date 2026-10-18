"""Learning loop tests: skill store + dreaming consolidation."""

import json

import pytest

from novapilot_learning import DreamConsolidator, Skill, SkillStore


@pytest.fixture()
def store(tmp_path):
    return SkillStore(tmp_path / "skills")


def test_save_get_roundtrip(store):
    s = Skill(
        name="Morning Brief",
        description="Summarize overnight news",
        instructions="1. Fetch feeds\n2. Summarize",
        tools=["web_fetch"],
        created_from=["t1"],
    )
    store.save(s)
    got = store.get("morning-brief")
    assert got is not None
    assert got.description == "Summarize overnight news"
    assert got.tools == ["web_fetch"]
    assert "Fetch feeds" in got.instructions


def test_skill_file_is_human_readable(store, tmp_path):
    store.save(Skill(name="x", description="d", instructions="do things"))
    text = (tmp_path / "skills" / "x" / "SKILL.md").read_text()
    assert text.startswith("---\n")
    assert "do things" in text


def test_list_and_delete(store):
    store.save(Skill(name="a", description="da", instructions="i"))
    store.save(Skill(name="b", description="db", instructions="i"))
    assert {s.name for s in store.list()} == {"a", "b"}
    assert store.delete("a") is True
    assert store.get("a") is None
    assert store.delete("missing") is False


def test_find_relevant(store):
    store.save(Skill(name="morning-brief", description="summarize overnight news feeds",
                     instructions="fetch rss"))
    store.save(Skill(name="deploy-app", description="deploy web app to server",
                     instructions="run deploy script"))
    hits = store.find_relevant("summarize the news for me")
    assert [s.name for s in hits] == ["morning-brief"]
    assert store.find_relevant("completely unrelated xyzzy") == []


def test_record_use(store):
    store.save(Skill(name="a", description="d", instructions="i"))
    store.record_use("a")
    assert store.get("a").use_count == 1


def test_bad_name_rejected():
    with pytest.raises(ValueError):
        SkillStore("/tmp/x").save(Skill(name="!!!", description="d", instructions="i"))


class _FakeGateway:
    def __init__(self, text):
        self.text = text

    async def chat(self, messages, model=None):
        return self.text


class _FakeMemory:
    def __init__(self):
        from types import SimpleNamespace

        self.saved = []
        self._ns = SimpleNamespace

    async def remember(self, namespace, content, tags=None, source=None):
        from types import SimpleNamespace

        mem = SimpleNamespace(id=f"m{len(self.saved)}", content=content)
        self.saved.append({"namespace": namespace, "content": content, "tags": tags, "source": source})
        return mem


async def test_dreaming_stores_facts():
    gw = _FakeGateway(json.dumps([
        {"content": "Syed prefers morning meetings.", "tags": ["preference"]},
        {"content": "", "tags": []},  # skipped
    ]))
    mem = _FakeMemory()
    d = DreamConsolidator(gw, mem, namespace="default")
    stored = await d.consolidate([
        {"goal": "schedule meeting", "summary": "Booked standup for 9am; Syed said mornings work best."},
    ])
    assert len(stored) == 1
    assert mem.saved[0]["source"] == "dreaming"
    assert mem.saved[0]["namespace"] == "default"


async def test_dreaming_empty_work():
    gw = _FakeGateway("[]")
    mem = _FakeMemory()
    d = DreamConsolidator(gw, mem)
    assert await d.consolidate([]) == []
    assert await d.consolidate([{"goal": "x", "summary": ""}]) == []


async def test_dreaming_bad_json_dropped():
    gw = _FakeGateway("not json at all")
    mem = _FakeMemory()
    d = DreamConsolidator(gw, mem)
    stored = await d.consolidate([{"goal": "x", "summary": "did stuff"}])
    assert stored == []
    assert mem.saved == []
