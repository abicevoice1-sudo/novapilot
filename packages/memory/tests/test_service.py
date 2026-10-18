"""MemoryService: CRUD, search, dedup, namespaces, export/import."""

import pytest

from novapilot_memory.service import MemoryService
from novapilot_memory.store import MemoryStore


@pytest.fixture()
async def svc(tmp_path):
    store = MemoryStore(str(tmp_path / "mem.db"))
    await store.init()
    yield MemoryService(store)
    await store.close()


async def test_remember_and_recall(svc):
    r = await svc.remember("u1", "Syed prefers morning meetings.", tags=["preference"])
    assert r["merged"] is False
    hits = await svc.recall("u1", "when does Syed like meetings")
    assert len(hits) == 1
    assert "morning meetings" in hits[0]["content"]


async def test_recall_empty(svc):
    assert await svc.recall("u1", "nothing here xyz") == []


async def test_dedup_merges(svc):
    await svc.remember("u1", "Syed prefers morning meetings.")
    r = await svc.remember("u1", "Syed prefers morning meetings for standup.", tags=["work"])
    assert r["merged"] is True
    memories, total = await svc.list_memories("u1")
    assert total == 1
    assert "work" in memories[0]["tags"]


async def test_namespaces_isolated(svc):
    await svc.remember("u1", "u1 likes chai")
    await svc.remember("u2", "u2 likes coffee")
    assert await svc.recall("u1", "coffee") == []
    assert len(await svc.recall("u2", "coffee")) == 1


async def test_update_and_delete(svc):
    r = await svc.remember("u1", "old fact")
    mid = r["memory"]["id"]
    updated = await svc.update_memory(mid, content="new fact")
    assert updated["content"] == "new fact"
    assert await svc.forget(mid) is True
    assert await svc.forget(mid) is False  # already gone


async def test_delete_honored_everywhere(svc):
    """Acceptance: deleting a memory removes it from search, list, recall."""
    r = await svc.remember("u1", "Syed's favorite editor is vim.")
    mid = r["memory"]["id"]
    assert len(await svc.recall("u1", "editor")) == 1
    await svc.forget(mid)
    assert await svc.recall("u1", "editor") == []
    memories, total = await svc.list_memories("u1")
    assert total == 0
    assert all(m["id"] != mid for m in memories)


async def test_secret_only_refused(svc):
    with pytest.raises(ValueError, match="bare secret"):
        await svc.remember("u1", "sk-abcdefghij1234567890xyz")


async def test_secret_redacted_on_write(svc):
    r = await svc.remember("u1", "api key is sk-abcdefghij1234567890xyz for project x")
    assert "[REDACTED]" in r["memory"]["content"]
    assert "sk-abcdefghij" not in r["memory"]["content"]


async def test_export_import_roundtrip(svc, tmp_path):
    await svc.remember("u1", "fact one", tags=["a"])
    await svc.remember("u1", "fact two")
    exported = await svc.export("u1")
    assert len(exported) == 2

    store2 = MemoryStore(str(tmp_path / "mem2.db"))
    await store2.init()
    svc2 = MemoryService(store2)
    try:
        result = await svc2.import_memories("u1", exported)
        assert result["added"] == 2
        assert await svc2.recall("u1", "fact one")
    finally:
        await store2.close()


async def test_import_skips_empties_and_secrets(svc):
    result = await svc.import_memories(
        "u1",
        [
            {"content": "good fact"},
            {"content": "   "},
            {"content": "sk-abcdefghij1234567890xyz"},
        ],
    )
    assert result == {"added": 1, "merged": 0, "skipped": 2}
