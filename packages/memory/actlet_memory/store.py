"""Embedded memory store: SQLite + FTS5. Zero services, works everywhere.

Schema is FTS-friendly; a vector column can be added later for hybrid search
without migrating existing rows.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import UTC, datetime

import aiosqlite

_SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    namespace TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]',
    source TEXT NOT NULL DEFAULT 'user',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_memories_namespace ON memories(namespace);
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(content, tags);
CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts(rowid, content, tags)
    VALUES (new.rowid, new.content, new.tags);
END;
CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
    DELETE FROM memories_fts WHERE rowid = old.rowid;
END;
CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
    DELETE FROM memories_fts WHERE rowid = old.rowid;
    INSERT INTO memories_fts(rowid, content, tags)
    VALUES (new.rowid, new.content, new.tags);
END;
"""


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _fts_query(query: str) -> str:
    """Turn free text into a safe FTS5 phrase query (no syntax injection)."""
    terms = re.findall(r"[A-Za-z0-9']{2,}", query.lower())
    if not terms:
        return '""'
    return " OR ".join(f'"{t}"' for t in terms[:12])


def _row_to_dict(row: aiosqlite.Row) -> dict:
    return {
        "id": row["id"],
        "namespace": row["namespace"],
        "content": row["content"],
        "tags": json.loads(row["tags"]),
        "source": row["source"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


class MemoryStore:
    def __init__(self, path: str = "./memories.db") -> None:
        self._path = path
        self._db: aiosqlite.Connection | None = None

    async def init(self) -> None:
        self._db = await aiosqlite.connect(self._path)
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(_SCHEMA)
        await self._db.commit()

    async def close(self) -> None:
        if self._db is not None:
            await self._db.close()
            self._db = None

    def _conn(self) -> aiosqlite.Connection:
        if self._db is None:
            raise RuntimeError("MemoryStore.init() not called")
        return self._db

    async def add(
        self, namespace: str, content: str, tags: list[str] | None = None, source: str = "user"
    ) -> dict:
        mid = uuid.uuid4().hex[:12]
        now = _now()
        tags_json = json.dumps(tags or [])
        db = self._conn()
        await db.execute(
            "INSERT INTO memories (id, namespace, content, tags, source, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (mid, namespace, content, tags_json, source, now, now),
        )
        await db.commit()
        return (await self.get(mid)) or {}

    async def get(self, mid: str) -> dict | None:
        db = self._conn()
        async with db.execute("SELECT * FROM memories WHERE id = ?", (mid,)) as cur:
            row = await cur.fetchone()
        return _row_to_dict(row) if row else None

    async def update(
        self, mid: str, content: str | None = None, tags: list[str] | None = None
    ) -> dict | None:
        existing = await self.get(mid)
        if existing is None:
            return None
        new_content = content if content is not None else existing["content"]
        new_tags = tags if tags is not None else existing["tags"]
        db = self._conn()
        await db.execute(
            "UPDATE memories SET content = ?, tags = ?, updated_at = ? WHERE id = ?",
            (new_content, json.dumps(new_tags), _now(), mid),
        )
        await db.commit()
        return await self.get(mid)

    async def delete(self, mid: str) -> bool:
        db = self._conn()
        cur = await db.execute("DELETE FROM memories WHERE id = ?", (mid,))
        await db.commit()
        return cur.rowcount > 0

    async def list(
        self, namespace: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[dict], int]:
        db = self._conn()
        async with db.execute(
            "SELECT COUNT(*) AS n FROM memories WHERE namespace = ?", (namespace,)
        ) as cur:
            total = (await cur.fetchone())["n"]
        async with db.execute(
            "SELECT * FROM memories WHERE namespace = ? ORDER BY updated_at DESC LIMIT ? OFFSET ?",
            (namespace, limit, offset),
        ) as cur:
            rows = await cur.fetchall()
        return [_row_to_dict(r) for r in rows], total

    async def search(self, namespace: str, query: str, limit: int = 5) -> list[dict]:
        db = self._conn()
        fts = _fts_query(query)
        async with db.execute(
            """
            SELECT m.*, rank AS _rank FROM memories_fts f
            JOIN memories m ON m.rowid = f.rowid
            WHERE memories_fts MATCH ? AND m.namespace = ?
            ORDER BY rank LIMIT ?
            """,
            (fts, namespace, limit),
        ) as cur:
            rows = await cur.fetchall()
        return [_row_to_dict(r) for r in rows]

    async def count(self, namespace: str) -> int:
        _, total = await self.list(namespace, limit=1)
        return total
