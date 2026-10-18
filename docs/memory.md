# Memory — policies and design

Nova's memory is **yours**: every memory is readable in the Memory page, editable,
deletable, and exportable. Deleting a memory removes it everywhere — search,
chat recall, the agent's tools, and exports. There is no hidden memory.

## What gets remembered

- **You ask:** "remember that I prefer morning meetings" → stored immediately.
- **You approve:** the "Remember this conversation" button extracts candidate facts
  with the model and stores them. Nothing is extracted silently.
- **The agent, during tasks:** the agent may `memory_add` low-sensitivity working
  facts (e.g. "the repo uses pnpm"). It may never store secrets (see below).

## Consent rules

| Action | Consent |
|---|---|
| Agent searches memory (`memory_search`) | Automatic — recall is the point |
| Agent adds a fact (`memory_add`) | Automatic for low-sensitivity facts during tasks |
| Agent deletes a memory (`memory_delete`) | **Requires your approval** (human gate) |
| Chat injects relevant memories into context | Automatic (read-only) |
| "Remember this conversation" extraction | **You click the button** |
| Export | You click export |

## Redaction (enforced, not suggested)

Every write path — API, agent tools, extraction, import — runs content through
the redactor before storage:

- API keys/tokens (`sk-…`, `ghp_…`, `xox…`, `AKIA…`, `password: …`) → `[REDACTED]`
- SSNs → `[REDACTED-SSN]`; card numbers → `[REDACTED-CARD]`
- If the *entire* content is a bare secret, the write is **refused** (400), not stored redacted.

## Storage

- Default: embedded SQLite + FTS5 (`MEMORY_PATH`, `./memories.db`), keyword search
  with BM25 ranking. Zero services, works on a laptop.
- Optional: `MEMORY_BACKEND=mem0` uses the real mem0 package against self-hosted
  Qdrant + Ollama (needs `pip install 'novapilot-memory[mem0]'`; see
  `novapilot_memory/backends/mem0_backend.py`). The service interface is identical,
  so switching backends never changes the API or UI.
- Namespaces: memories live under a namespace (`MEMORY_NAMESPACE`, default
  `"default"`); namespaces are fully isolated for future multi-user support.

## Deduplication

Adding a near-duplicate fact merges into the existing memory (tags unioned)
instead of creating a second row. The API reports `"merged": true` when this happens.
