"""Tool registry: validated, risk-tiered, receipted tool calls.

Every tool declares a pydantic args schema, a risk tier, and whether it needs
human approval. Calls are validated before execution, timed, and wrapped in a
signed-style receipt (tool, args, duration, outcome).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import shlex
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path

import httpx
from pydantic import BaseModel, Field, ValidationError

log = logging.getLogger("novapilot.tools")

DEFAULT_TIMEOUT_SEC = 120
MAX_FETCH_CHARS = 8000

# shell tool: read-only allowlist (full shell arrives with the Docker sandbox in M5)
SHELL_ALLOWLIST = {
    "ls", "cat", "head", "tail", "wc", "find", "grep", "echo",
    "pwd", "date", "du", "df", "whoami", "uname", "sort", "uniq",
}


@dataclass
class ToolResult:
    ok: bool
    output: str
    verification: str = ""
    duration_ms: int = 0
    artifacts: dict = field(default_factory=dict)  # e.g. {"shot": "shots/shot-0001.png"}


@dataclass
class Tool:
    name: str
    description: str
    args_schema: type[BaseModel]
    func: Callable[[BaseModel], Awaitable[ToolResult]]
    risk: str = "low"  # low | medium | high
    requires_approval: bool = False
    timeout_sec: int = DEFAULT_TIMEOUT_SEC


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def subset(self, names: list[str]) -> ToolRegistry:
        """A new registry with only the named tools (missing names ignored)."""
        sub = ToolRegistry()
        for name in names:
            tool = self._tools.get(name)
            if tool is not None:
                sub.register(tool)
        return sub

    def specs(self) -> list[dict]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "risk": t.risk,
                "requires_approval": t.requires_approval,
                "args_schema": t.args_schema.model_json_schema(),
            }
            for t in self._tools.values()
        ]

    def validate(self, name: str, raw_args: dict) -> BaseModel:
        """Validate args against the tool's schema. Raises ValueError."""
        tool = self.get(name)
        if tool is None:
            raise ValueError(f"unknown tool: {name}")
        try:
            return tool.args_schema(**(raw_args or {}))
        except ValidationError as e:
            raise ValueError(f"invalid args for {name}: {e.errors()}") from e

    async def call(self, name: str, raw_args: dict) -> tuple[ToolResult, dict]:
        """Validated call. Returns (result, receipt). Never raises for tool errors."""
        tool = self.get(name)
        if tool is None:
            return ToolResult(ok=False, output=f"unknown tool: {name}"), self._receipt(
                name, raw_args, False, 0
            )
        try:
            args = self.validate(name, raw_args)
        except ValueError as e:
            return ToolResult(ok=False, output=str(e)), self._receipt(name, raw_args, False, 0)
        start = time.monotonic()
        try:
            result = await asyncio.wait_for(tool.func(args), timeout=tool.timeout_sec)
        except TimeoutError:
            result = ToolResult(ok=False, output=f"timed out after {tool.timeout_sec}s")
        except Exception as e:
            log.exception("tool %s raised", name)
            result = ToolResult(ok=False, output=f"tool error: {type(e).__name__}: {e}")
        duration_ms = int((time.monotonic() - start) * 1000)
        result.duration_ms = duration_ms
        return result, self._receipt(name, raw_args, result.ok, duration_ms)

    @staticmethod
    def _receipt(name: str, args: dict, ok: bool, duration_ms: int) -> dict:
        digest = hashlib.sha256(json.dumps(args, sort_keys=True, default=str).encode()).hexdigest()[:16]
        return {
            "tool": name,
            "args_digest": digest,
            "ok": ok,
            "duration_ms": duration_ms,
            "ts": time.time(),
        }


# ---------------------------------------------------------------- built-in tools

class _PathArgs(BaseModel):
    path: str = Field(description="Path relative to the workspace root")


class _WriteArgs(BaseModel):
    path: str = Field(description="Path relative to the workspace root")
    content: str = Field(description="File content to write")


class _FetchArgs(BaseModel):
    url: str = Field(description="http(s) URL to fetch as text")
    max_chars: int = Field(default=MAX_FETCH_CHARS, le=50000)


class _ShellArgs(BaseModel):
    command: str = Field(description="Read-only shell command (allowlisted)")


def _workspace() -> Path:
    import os

    root = Path(os.environ.get("NOVAPILOT_WORKSPACE", "./workspace")).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _resolve(path: str) -> Path:
    """Resolve a workspace-relative path; block escapes."""
    root = _workspace()
    target = (root / path).resolve()
    if not target.is_relative_to(root):
        raise ValueError(f"path escapes workspace: {path}")
    return target


async def _read_file(args: _PathArgs) -> ToolResult:
    p = _resolve(args.path)
    if not p.is_file():
        return ToolResult(ok=False, output=f"not a file: {args.path}")
    text = p.read_text(encoding="utf-8", errors="replace")
    return ToolResult(
        ok=True,
        output=text[:20000],
        verification=f"read {len(text)} chars from {args.path}",
    )


async def _list_dir(args: _PathArgs) -> ToolResult:
    p = _resolve(args.path or ".")
    if not p.is_dir():
        return ToolResult(ok=False, output=f"not a directory: {args.path}")
    names = sorted(x.name + ("/" if x.is_dir() else "") for x in p.iterdir())
    return ToolResult(ok=True, output="\n".join(names), verification=f"listed {len(names)} entries")


async def _write_file(args: _WriteArgs) -> ToolResult:
    p = _resolve(args.path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(args.content, encoding="utf-8")
    back = p.read_text(encoding="utf-8")
    ok = back == args.content
    return ToolResult(
        ok=ok,
        output=f"wrote {len(args.content)} chars to {args.path}",
        verification=f"read-back matches: {ok}",
    )


async def _web_fetch(args: _FetchArgs) -> ToolResult:
    if not args.url.startswith(("http://", "https://")):
        return ToolResult(ok=False, output="only http(s) URLs allowed")
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            r = await client.get(args.url, headers={"User-Agent": "NovaPilot/0.3 (+research)"})
    except Exception as e:  # noqa: BLE001
        return ToolResult(ok=False, output=f"fetch failed: {type(e).__name__}: {e}")
    if r.status_code != 200:
        return ToolResult(ok=False, output=f"HTTP {r.status_code} for {args.url}")
    text = r.text
    # crude HTML → text
    import re

    text = re.sub(r"<script.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return ToolResult(
        ok=True,
        output=text[: args.max_chars],
        verification=f"HTTP 200, extracted {min(len(text), args.max_chars)} chars",
    )


async def _shell(args: _ShellArgs) -> ToolResult:
    parts = shlex.split(args.command)
    if not parts or parts[0] not in SHELL_ALLOWLIST:
        return ToolResult(
            ok=False,
            output=f"command not allowlisted (M3 shell is read-only): {parts[0] if parts else ''}",
        )
    try:
        proc = await asyncio.create_subprocess_exec(
            *parts,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(_workspace()),
        )
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
    except TimeoutError:
        return ToolResult(ok=False, output="timed out after 30s")
    text = out.decode("utf-8", errors="replace")[:10000]
    return ToolResult(
        ok=proc.returncode == 0,
        output=text,
        verification=f"exit code {proc.returncode}",
    )


class _SandboxShellArgs(BaseModel):
    command: str = Field(description="Shell command to run inside the Docker sandbox")
    timeout_sec: int = Field(default=60, ge=5, le=300)


async def _shell_sandboxed(args: _SandboxShellArgs) -> ToolResult:
    """Full shell inside a locked-down Docker container (needs approval)."""
    from .sandbox import DockerSandbox

    sandbox = DockerSandbox()
    try:
        result = await asyncio.to_thread(
            sandbox.run, args.command, str(_workspace()), args.timeout_sec
        )
    except RuntimeError as e:
        return ToolResult(ok=False, output=str(e))
    out = result.stdout
    if result.stderr:
        out += f"\n[stderr]\n{result.stderr}"
    if result.truncated:
        out += "\n[truncated]"
    return ToolResult(
        ok=result.returncode == 0,
        output=out,
        verification=f"exit code {result.returncode} (docker sandbox)",
    )


def sandboxed_shell_available() -> bool:
    """True when NOVAPILOT_SANDBOX=docker and Docker is reachable."""
    import os

    if os.environ.get("NOVAPILOT_SANDBOX", "").lower() != "docker":
        return False
    from .sandbox import DockerSandbox

    return DockerSandbox.available()


def builtin_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(Tool("read_file", "Read a text file from the workspace", _PathArgs, _read_file))
    reg.register(Tool("list_dir", "List a workspace directory", _PathArgs, _list_dir))
    reg.register(
        Tool(
            "write_file",
            "Write a text file in the workspace (needs approval)",
            _WriteArgs,
            _write_file,
            risk="medium",
            requires_approval=True,
        )
    )
    reg.register(Tool("web_fetch", "Fetch a web page as text (read-only)", _FetchArgs, _web_fetch))
    reg.register(
        Tool("shell", "Run a read-only allowlisted shell command", _ShellArgs, _shell)
    )
    if sandboxed_shell_available():
        reg.register(
            Tool(
                "shell_sandboxed",
                "Run a full shell command inside a locked-down Docker container "
                "(no network, capped resources). Needs approval.",
                _SandboxShellArgs,
                _shell_sandboxed,
                risk="high",
                requires_approval=True,
            )
        )
    return reg
