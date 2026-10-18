"""Tool registry: validation, sandboxing, allowlists."""


import pytest
from pydantic import BaseModel

from novapilot_agent.tools import Tool, ToolRegistry, ToolResult, builtin_registry


class _Args(BaseModel):
    text: str


async def _echo(args: _Args) -> ToolResult:
    return ToolResult(ok=True, output=args.text, verification="echoed")


def test_validate_rejects_unknown_tool():
    reg = ToolRegistry()
    with pytest.raises(ValueError, match="unknown tool"):
        reg.validate("nope", {})


def test_validate_rejects_bad_args():
    reg = ToolRegistry()
    reg.register(Tool("echo", "echo", _Args, _echo))
    with pytest.raises(ValueError, match="invalid args"):
        reg.validate("echo", {"wrong": 1})


async def test_call_unknown_tool_returns_failure_not_exception():
    reg = ToolRegistry()
    result, receipt = await reg.call("nope", {})
    assert result.ok is False
    assert receipt["tool"] == "nope"


async def test_shell_allowlist_blocks_dangerous_commands():
    reg = builtin_registry()
    result, _ = await reg.call("shell", {"command": "rm -rf /"})
    assert result.ok is False
    assert "allowlisted" in result.output


async def test_shell_allowlist_permits_safe_commands(tmp_path, monkeypatch):
    monkeypatch.setenv("NOVAPILOT_WORKSPACE", str(tmp_path))
    reg = builtin_registry()
    result, receipt = await reg.call("shell", {"command": "echo hello"})
    assert result.ok is True
    assert "hello" in result.output
    assert receipt["ok"] is True
    assert len(receipt["args_digest"]) == 16


async def test_write_file_confined_to_workspace(tmp_path, monkeypatch):
    monkeypatch.setenv("NOVAPILOT_WORKSPACE", str(tmp_path))
    reg = builtin_registry()
    result, _ = await reg.call("write_file", {"path": "../../escape.txt", "content": "x"})
    assert result.ok is False
    assert "escapes workspace" in result.output


async def test_write_file_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("NOVAPILOT_WORKSPACE", str(tmp_path))
    reg = builtin_registry()
    result, _ = await reg.call("write_file", {"path": "sub/note.txt", "content": "hello"})
    assert result.ok is True
    assert "read-back matches: True" in result.verification
    assert (tmp_path / "sub" / "note.txt").read_text() == "hello"


async def test_write_file_requires_approval():
    reg = builtin_registry()
    assert reg.get("write_file").requires_approval is True
    assert reg.get("read_file").requires_approval is False


def test_specs_expose_json_schema():
    reg = builtin_registry()
    specs = {s["name"]: s for s in reg.specs()}
    assert "write_file" in specs
    assert "content" in specs["write_file"]["args_schema"]["properties"]
