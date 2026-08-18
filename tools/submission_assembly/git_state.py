"""Read-only Git state checks for role-candidate assembly."""

from __future__ import annotations

import subprocess
from pathlib import Path


def require_clean_worktree(repo_root: Path) -> None:
    """Refuse candidate assembly from a dirty tracked or untracked source tree."""
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={repo_root.as_posix()}",
            "-C",
            str(repo_root),
            "status",
            "--porcelain",
            "--untracked-files=all",
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.stdout:
        raise ValueError("source worktree must be clean before candidate assembly")
