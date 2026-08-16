"""escapes_root must fail closed on a symlink pointing outside root."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.offline_ops.fs_safety import escapes_root


def test_a_plain_descendant_does_not_escape(tmp_path: Path) -> None:
    child = tmp_path / "file.txt"
    child.write_text("x", encoding="utf-8")
    assert not escapes_root(tmp_path, child)


def test_a_symlink_escaping_root_is_detected(tmp_path: Path) -> None:
    outside = tmp_path.parent / "fs_safety_outside.txt"
    outside.write_text("x", encoding="utf-8")
    root = tmp_path / "root"
    root.mkdir()
    link = root / "escape.txt"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation requires elevated privilege on this platform")
    try:
        assert escapes_root(root, link)
    finally:
        outside.unlink(missing_ok=True)
