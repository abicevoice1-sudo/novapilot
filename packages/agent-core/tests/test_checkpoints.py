"""Workspace checkpoint tests: snapshot before risky steps, revert on demand."""

import pytest

from actlet_agent import CheckpointManager


@pytest.fixture()
def mgr(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    (ws / "notes.txt").write_text("original")
    (ws / "sub").mkdir()
    (ws / "sub" / "data.txt").write_text("data")
    return CheckpointManager(ws), ws


def test_snapshot_restore_roundtrip(mgr):
    manager, ws = mgr
    manager.snapshot("t1", "s1")
    (ws / "notes.txt").write_text("modified")
    (ws / "new.txt").write_text("new file")
    manager.restore("t1", "s1")
    assert (ws / "notes.txt").read_text() == "original"
    assert not (ws / "new.txt").exists()
    assert (ws / "sub" / "data.txt").read_text() == "data"


def test_restore_missing_raises(mgr):
    manager, _ = mgr
    with pytest.raises(ValueError, match="no checkpoint"):
        manager.restore("t1", "nope")


def test_latest_and_list(mgr):
    manager, _ = mgr
    assert manager.latest("t1") is None
    assert manager.list("t1") == []
    manager.snapshot("t1", "s1")
    manager.snapshot("t1", "s2")
    assert manager.latest("t1") == "s2"
    assert sorted(manager.list("t1")) == ["s1", "s2"]


def test_checkpoints_dir_excluded(mgr):
    manager, ws = mgr
    manager.snapshot("t1", "s1")
    # Snapshots must not nest inside each other.
    snap_files = list((ws / ".checkpoints").rglob("*"))
    assert not any(".checkpoints" in str(p.relative_to(ws / ".checkpoints")) for p in snap_files
                   if p.is_dir() and p.name == ".checkpoints")


def test_malicious_ids_sanitized(mgr):
    manager, ws = mgr
    manager.snapshot("../../evil", "s1")
    # Must stay inside the checkpoints dir.
    assert (ws / ".checkpoints").resolve() in (ws / ".checkpoints" / "evil").resolve().parents
