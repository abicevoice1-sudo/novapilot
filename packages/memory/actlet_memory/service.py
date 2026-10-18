"""MemoryService: the policy layer over the store.

- Every write is redacted; secret-only content is refused.
- Dedup: near-duplicate memories are merged, not duplicated.
- Delete is honored everywhere (single source of truth: the store).
"""

from __future__ import annotations

import logging
import os
import re

from .redact import looks_like_secret_only, redact
from .store import MemoryStore

log = logging.getLogger("actlet.memory")

_STOPWORDS = frozenset(
    ["a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "with", "is", "are", "was", "were", "be", "been", "i", "me", "my", "you", "your", "he", "she", "it", "we", "they", "them", "this", "that", "these", "those", "as", "at", "by", "from"]
)


def _sig_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9']{3,}", text.lower()) if w not in _STOPWORDS}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class MemoryService:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    async def remember(
        self,
        namespace: str,
        content: str,
        tags: list[str] | None = None,
        source: str = "user",
    ) -> dict:
        """Store a memory. Returns {memory, merged} — merged=True if deduped."""
        content = content.strip()
        if not content:
            raise ValueError("empty memory")
        if looks_like_secret_only(content):
            raise ValueError("refused: content is a bare secret")
        content = redact(content)

        # dedup: merge into a near-duplicate instead of doubling it
        candidates = await self.store.search(namespace, content, limit=3)
        new_sig = _sig_words(content)
        for cand in candidates:
            if _jaccard(new_sig, _sig_words(cand["content"])) >= 0.6:
                merged_tags = sorted(set(cand["tags"]) | set(tags or []))
                updated = await self.store.update(cand["id"], content=content, tags=merged_tags)
                log.info("memory deduped into %s", cand["id"])
                return {"memory": updated, "merged": True}

        memory = await self.store.add(namespace, content, tags, source)
        return {"memory": memory, "merged": False}

    async def recall(self, namespace: str, query: str, limit: int = 5) -> list[dict]:
        return await self.store.search(namespace, query, limit=limit)

    async def list_memories(
        self, namespace: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[dict], int]:
        return await self.store.list(namespace, limit=limit, offset=offset)

    async def update_memory(
        self, mid: str, content: str | None = None, tags: list[str] | None = None
    ) -> dict | None:
        if content is not None:
            if looks_like_secret_only(content):
                raise ValueError("refused: content is a bare secret")
            content = redact(content)
        return await self.store.update(mid, content=content, tags=tags)

    async def forget(self, mid: str) -> bool:
        """Delete a memory. The store is the single source of truth, so the
        memory is gone from search, recall, list, and export everywhere."""
        return await self.store.delete(mid)

    async def export(self, namespace: str) -> list[dict]:
        memories, _ = await self.store.list(namespace, limit=10_000)
        return [
            {"content": m["content"], "tags": m["tags"], "source": m["source"]}
            for m in memories
        ]

    async def import_memories(self, namespace: str, items: list[dict]) -> dict:
        added, skipped, merged = 0, 0, 0
        for item in items:
            content = (item.get("content") or "").strip()
            if not content:
                skipped += 1
                continue
            try:
                result = await self.remember(
                    namespace, content, tags=item.get("tags") or [], source="import"
                )
            except ValueError:
                skipped += 1
                continue
            if result["merged"]:
                merged += 1
            else:
                added += 1
        return {"added": added, "merged": merged, "skipped": skipped}


def create_service() -> MemoryService:
    """Factory honoring MEMORY_BACKEND (default 'embedded')."""
    backend = os.environ.get("MEMORY_BACKEND", "embedded")
    if backend == "mem0":
        from .backends.mem0_backend import Mem0MemoryService

        return Mem0MemoryService()
    path = os.environ.get("MEMORY_PATH", "./memories.db")
    return MemoryService(MemoryStore(path))
