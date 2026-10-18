"""Docker sandbox tests: command construction + graceful degradation.

Docker is NOT available in CI/this VM, so these verify the interface and
the fallback behavior — never a real container.
"""

from unittest.mock import patch

from actlet_agent.sandbox import DockerSandbox, SandboxResult
from actlet_agent.tools import builtin_registry, sandboxed_shell_available


def test_available_false_without_docker():
    with patch("shutil.which", return_value=None):
        assert DockerSandbox.available() is False


def test_sandboxed_tool_not_registered_by_default(monkeypatch):
    monkeypatch.delenv("ACTLET_SANDBOX", raising=False)
    reg = builtin_registry()
    assert reg.get("shell_sandboxed") is None
    assert sandboxed_shell_available() is False


def test_docker_command_construction():
    sandbox = DockerSandbox(image="python:3.12-slim", memory="256m", cpus="0.5")
    captured = {}

    class _Proc:
        returncode = 0
        stdout = "hi\n"
        stderr = ""

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return _Proc()

    with patch("subprocess.run", side_effect=fake_run), \
         patch.object(DockerSandbox, "available", return_value=True):
        result = sandbox.run("echo hi", "/work/dir", timeout_sec=10)

    cmd = captured["cmd"]
    assert cmd[:3] == ["docker", "run", "--rm"]
    assert "--network" in cmd and "none" in cmd
    assert "--read-only" in cmd
    assert "/work/dir:/work" in cmd
    assert cmd[-3:] == ["sh", "-c", "echo hi"]
    assert isinstance(result, SandboxResult)
    assert result.returncode == 0 and result.stdout == "hi\n"


def test_run_raises_when_unavailable():
    with patch.object(DockerSandbox, "available", return_value=False):
        try:
            DockerSandbox().run("echo hi", "/tmp")
            raise AssertionError("should have raised")
        except RuntimeError as e:
            assert "Docker is not available" in str(e)


async def test_sandboxed_tool_fails_cleanly_without_docker(monkeypatch):
    monkeypatch.delenv("ACTLET_SANDBOX", raising=False)
    # Register the tool manually to test its error path.

    from actlet_agent.tools import Tool, ToolRegistry, _SandboxShellArgs, _shell_sandboxed

    reg = ToolRegistry()
    reg.register(Tool("shell_sandboxed", "x", _SandboxShellArgs, _shell_sandboxed,
                      risk="high", requires_approval=True))
    result, _ = await reg.call("shell_sandboxed", {"command": "echo hi"})
    assert result.ok is False
    assert "Docker is not available" in result.output
