"""Docker sandbox: run shell commands in a locked-down container.

When ACTLET_SANDBOX=docker and Docker is available, the agent's shell
tool runs inside a container instead of the allowlist:
- workspace mounted at /work (read-write; the agent's files live there)
- no network (--network none)
- memory/CPU capped, read-only root FS with a writable /tmp
- container removed after every command (--rm)

Requires Docker at runtime; falls back to the read-only allowlist otherwise
(with a clear warning — never silently).
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from dataclasses import dataclass

log = logging.getLogger("actlet.sandbox")


@dataclass
class SandboxResult:
    returncode: int
    stdout: str
    stderr: str
    truncated: bool = False


class DockerSandbox:
    def __init__(
        self,
        image: str = "python:3.12-slim",
        memory: str = "512m",
        cpus: str = "1.0",
    ) -> None:
        self.image = image
        self.memory = memory
        self.cpus = cpus

    @staticmethod
    def available() -> bool:
        """Is a working Docker daemon reachable?"""
        if shutil.which("docker") is None:
            return False
        try:
            r = subprocess.run(
                ["docker", "info"], capture_output=True, timeout=10, check=False
            )
            return r.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            return False

    def run(self, command: str, workspace: str, timeout_sec: int = 60) -> SandboxResult:
        """Run a shell command in the sandbox. Raises RuntimeError if unavailable."""
        if not self.available():
            raise RuntimeError("Docker is not available for sandboxed execution")
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{workspace}:/work",
            "-w", "/work",
            "--network", "none",
            "--memory", self.memory,
            "--cpus", self.cpus,
            "--read-only",
            "--tmpfs", "/tmp:rw,size=64m",
            self.image,
            "sh", "-c", command,
        ]
        try:
            proc = subprocess.run(
                docker_cmd, capture_output=True, text=True,
                timeout=timeout_sec, check=False,
            )
        except subprocess.TimeoutExpired as e:
            return SandboxResult(
                returncode=124,
                stdout=(e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or ""),
                stderr="sandbox: command timed out",
                truncated=True,
            )
        out, err = proc.stdout, proc.stderr
        truncated = False
        if len(out) > 20000:
            out, truncated = out[:20000], True
        if len(err) > 5000:
            err, truncated = err[:5000], True
        return SandboxResult(
            returncode=proc.returncode, stdout=out, stderr=err, truncated=truncated
        )
