"""NovaPilot memory: the user owns it, reads it, and can delete it.

Default backend is embedded SQLite + FTS5 (zero services, works everywhere).
A mem0 adapter is available for self-hosted mem0+Qdrant+Ollama setups.
"""

from .redact import looks_like_secret_only, redact
from .service import MemoryService, create_service
from .store import MemoryStore

__all__ = [
    "MemoryService",
    "MemoryStore",
    "create_service",
    "looks_like_secret_only",
    "redact",
]
