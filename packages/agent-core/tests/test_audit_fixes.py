"""Audit-fix security tests: shell hardening, SSRF, workspace isolation."""

import pytest

from actlet_agent.tools import (
    _is_public_ip,
    _check_url_public,
    _shell,
    _ShellArgs,
    builtin_registry,
)


async def test_shell_rejects_parent_escape(tmp_path):
    reg = builtin_registry(workspace_dir=str(tmp_path))
    tool = next(t for t in reg._tools.values() if t.name == "shell")
    result, _ = await reg.call("shell", {"command": "cat ../.env"})
    assert result.ok is False
    assert "escapes workspace" in result.output


async def test_shell_rejects_absolute_path(tmp_path):
    reg = builtin_registry(workspace_dir=str(tmp_path))
    result, _ = await reg.call("shell", {"command": "cat /etc/passwd"})
    assert result.ok is False
    assert "escapes workspace" in result.output


async def test_shell_rejects_metacharacters(tmp_path):
    reg = builtin_registry(workspace_dir=str(tmp_path))
    result, _ = await reg.call("shell", {"command": "ls | cat"})
    assert result.ok is False


async def test_shell_requires_approval(tmp_path):
    reg = builtin_registry(workspace_dir=str(tmp_path))
    tool = next(t for t in reg._tools.values() if t.name == "shell")
    assert tool.requires_approval is True
    assert tool.risk == "medium"


async def test_shell_runs_in_workspace(tmp_path):
    (tmp_path / "hello.txt").write_text("hi")
    reg = builtin_registry(workspace_dir=str(tmp_path))
    result, _ = await reg.call("shell", {"command": "cat hello.txt"})
    assert result.ok is True
    assert "hi" in result.output


async def test_shell_scrubs_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("ACTLET_TOKEN", "super-secret-token")
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "super-secret-pw")
    reg = builtin_registry(workspace_dir=str(tmp_path))
    result, _ = await reg.call("shell", {"command": "echo ok"})
    assert result.ok is True
    # The child process cannot see parent secrets (it only gets PATH/HOME).
    result2, _ = await reg.call("shell", {"command": "echo $ACTLET_TOKEN"})
    assert "super-secret-token" not in result2.output


def test_ssrf_blocks_loopback():
    assert _is_public_ip("127.0.0.1") is False
    assert _is_public_ip("::1") is False


def test_ssrf_blocks_private():
    assert _is_public_ip("192.168.1.1") is False
    assert _is_public_ip("10.0.0.1") is False
    assert _is_public_ip("172.16.0.1") is False


def test_ssrf_blocks_link_local():
    assert _is_public_ip("169.254.169.254") is False


def test_ssrf_allows_public():
    assert _is_public_ip("8.8.8.8") is True
    assert _is_public_ip("1.1.1.1") is True


def test_url_check_blocks_localhost():
    err = _check_url_public("http://localhost:8000/api")
    assert err is not None and "non-public" in err


def test_url_check_blocks_127():
    err = _check_url_public("http://127.0.0.1:8000/")
    assert err is not None and "non-public" in err


async def test_web_fetch_blocks_ssrf():
    reg = builtin_registry()
    result, _ = await reg.call("web_fetch", {"url": "http://127.0.0.1:8000/"})
    assert result.ok is False
    assert "non-public" in result.output


async def test_workspace_canonical_injection(tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    (tmp_path / "a.txt").write_text("canonical")
    (other / "b.txt").write_text("wrong")
    reg = builtin_registry(workspace_dir=str(tmp_path))
    result, _ = await reg.call("read_file", {"path": "a.txt"})
    assert result.ok is True
    # Cannot reach the other directory even via ..
    result2, _ = await reg.call("read_file", {"path": "../other/b.txt"})
    assert result2.ok is False
