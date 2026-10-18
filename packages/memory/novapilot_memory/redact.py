"""Redaction: secrets never enter memory.

Applied to every write path (API, agent tools, extraction). If the entire
content is just a secret value, the write is refused outright.
"""

from __future__ import annotations

import re

# (pattern, replacement)
_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"sk-ant-[A-Za-z0-9-]{20,}"), "[REDACTED]"),  # Anthropic
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "[REDACTED]"),  # OpenAI-style
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "[REDACTED]"),  # GitHub
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "[REDACTED]"),  # GitHub fine-grained
    (re.compile(r"xox[bap]-?[A-Za-z0-9-]{10,}"), "[REDACTED]"),  # Slack
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED]"),  # AWS access key
    (
        re.compile(
            r"(?i)(password|passwd|pwd|api[_-]?key|secret|token|bearer)\s*[:=]\s*['\"]?\S+['\"]?"
        ),
        r"\1=[REDACTED]",
    ),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED-SSN]"),
    (re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"), "[REDACTED-CARD]"),
]

# If the whole content matches one of these, refuse the write entirely.
_SECRET_ONLY = [
    re.compile(r"^(sk-ant-|sk-)[A-Za-z0-9-]{20,}$"),
    re.compile(r"^ghp_[A-Za-z0-9]{20,}$"),
    re.compile(r"^github_pat_[A-Za-z0-9_]{20,}$"),
    re.compile(r"^xox[bap]-?[A-Za-z0-9-]{10,}$"),
    re.compile(r"^AKIA[0-9A-Z]{16}$"),
]


def redact(text: str) -> str:
    """Replace secret values with [REDACTED] markers. Never raises."""
    out = text
    for pattern, replacement in _PATTERNS:
        out = pattern.sub(replacement, out)
    return out


def looks_like_secret_only(text: str) -> bool:
    """True if the content is nothing but a secret value (refuse to store)."""
    stripped = text.strip().strip("\"'")
    return any(p.match(stripped) for p in _SECRET_ONLY)
