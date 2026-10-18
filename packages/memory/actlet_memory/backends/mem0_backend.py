"""Optional mem0 backend: use the real mem0 package against self-hosted services.

Enable with MEMORY_BACKEND=mem0. Requires:
    pip install 'actlet-memory[mem0]'
    Qdrant running (MEM0_QDRANT_URL, default http://localhost:6333)
    An LLM for extraction (Ollama recommended: MEM0_LLM_BASE_URL)

This adapter is code-complete but NOT tested in CI (needs the services above).
The embedded SQLite+FTS5 backend is the default and is fully tested.
"""

from __future__ import annotations

import os


class Mem0MemoryService:
    """MemoryService-compatible facade over mem0's self-hosted client."""

    def __init__(self) -> None:
        try:
            from mem0 import Memory
        except ImportError as e:
            raise RuntimeError(
                "MEMORY_BACKEND=mem0 needs the mem0 extra: pip install 'actlet-memory[mem0]'"
            ) from e

        self._client = Memory.from_config(
            {
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "url": os.environ.get("MEM0_QDRANT_URL", "http://localhost:6333"),
                        "collection_name": "actlet_memory",
                    },
                },
                "llm": {
                    "provider": "ollama",
                    "config": {
                        "model": os.environ.get("MEM0_LLM_MODEL", "gpt-oss:20b"),
                        "ollama_base_url": os.environ.get(
                            "MEM0_LLM_BASE_URL", "http://localhost:11434"
                        ),
                    },
                },
                "embedder": {
                    "provider": "ollama",
                    "config": {
                        "model": os.environ.get("MEM0_EMBED_MODEL", "nomic-embed-text"),
                        "ollama_base_url": os.environ.get(
                            "MEM0_LLM_BASE_URL", "http://localhost:11434"
                        ),
                    },
                },
            }
        )

    # -- MemoryService-compatible surface (sync mem0 client wrapped) --
    async def remember(self, namespace, content, tags=None, source="user"):
        import asyncio

        result = await asyncio.to_thread(
            self._client.add, content, user_id=namespace, metadata={"tags": tags or [], "source": source}
        )
        mem = (result.get("results") or [{}])[0]
        return {"memory": {"id": mem.get("id"), "content": content}, "merged": False}

    async def recall(self, namespace, query, limit=5):
        import asyncio

        hits = await asyncio.to_thread(self._client.search, query, user_id=namespace, limit=limit)
        return [
            {"id": h.get("id"), "content": h.get("memory"), "tags": [], "source": "mem0"}
            for h in (hits.get("results") or [])
        ]

    async def list_memories(self, namespace, limit=50, offset=0):
        import asyncio

        all_mems = await asyncio.to_thread(self._client.get_all, user_id=namespace)
        items = [
            {"id": m.get("id"), "content": m.get("memory"), "tags": [], "source": "mem0"}
            for m in (all_mems.get("results") or [])
        ]
        return items[offset : offset + limit], len(items)

    async def update_memory(self, mid, content=None, tags=None):
        import asyncio

        await asyncio.to_thread(self._client.update, mid, content or "")
        return {"id": mid, "content": content}

    async def forget(self, mid):
        import asyncio

        await asyncio.to_thread(self._client.delete, mid)
        return True

    async def export(self, namespace):
        items, _ = await self.list_memories(namespace, limit=10_000)
        return [{"content": m["content"], "tags": m["tags"], "source": m["source"]} for m in items]

    async def import_memories(self, namespace, items):
        added = 0
        for item in items:
            if (item.get("content") or "").strip():
                await self.remember(namespace, item["content"], tags=item.get("tags") or [], source="import")
                added += 1
        return {"added": added, "merged": 0, "skipped": len(items) - added}
