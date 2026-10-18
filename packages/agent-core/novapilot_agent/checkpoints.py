"""Workspace checkpoints: snapshot before risky steps, revert on demand.

Snapshots live under <workspace>/.checkpoints/<task_id>/<step_id>/. Only the
workspace files are copied (never the checkpoints dir itself).
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

log = logging.getLogger("novapilot.checkpoints")


class CheckpointManager:
    def __init__(self, workspace_dir: str | Path) -> None:
        self.workspace = Path(workspace_dir)
        self.root = self.workspace / ".checkpoints"
        self.root.mkdir(parents=True, exist_ok=True)

    def _snap_dir(self, task_id: str, step_id: str) -> Path:
        # task_id/step_id are hex; no traversal risk, but stay defensive.
        safe_task = "".join(c for c in task_id if c.isalnum() or c in "-_")[:64]
        safe_step = "".join(c for c in step_id if c.isalnum() or c in "-_")[:64]
        return self.root / safe_task / safe_step

    def snapshot(self, task_id: str, step_id: str) -> Path:
        """Copy the workspace (minus checkpoints) to a snapshot dir."""
        dest = self._snap_dir(task_id, step_id)
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)
        for item in self.workspace.iterdir():
            if item.name == ".checkpoints":
                continue
            target = dest / item.name
            if item.is_dir():
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)
        log.info("checkpoint: task %s step %s -> %s", task_id, step_id, dest)
        return dest

    def restore(self, task_id: str, step_id: str) -> None:
        """Restore the workspace from a snapshot (destructive — by design)."""
        src = self._snap_dir(task_id, step_id)
        if not src.is_dir():
            raise ValueError(f"no checkpoint for task {task_id} step {step_id}")
        for item in self.workspace.iterdir():
            if item.name == ".checkpoints":
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        for item in src.iterdir():
            target = self.workspace / item.name
            if item.is_dir():
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)
        log.info("checkpoint: restored task %s step %s", task_id, step_id)

    def latest(self, task_id: str) -> str | None:
        """Most recent snapshot's step id, or None."""
        task_dir = self.root / "".join(c for c in task_id if c.isalnum() or c in "-_")[:64]
        if not task_dir.is_dir():
            return None
        snaps = sorted(
            (p for p in task_dir.iterdir() if p.is_dir()),
            key=lambda p: p.stat().st_mtime,
        )
        return snaps[-1].name if snaps else None

    def list(self, task_id: str) -> list[str]:
        task_dir = self.root / "".join(c for c in task_id if c.isalnum() or c in "-_")[:64]
        if not task_dir.is_dir():
            return []
        return sorted(p.name for p in task_dir.iterdir() if p.is_dir())
