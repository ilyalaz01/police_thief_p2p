"""Read-only Git index queries used by the submission exporter.

All subprocess calls are read-only local git commands with no network I/O.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def get_head_commit(repo_root: Path) -> str:
    """Return the current HEAD SHA as a 40-character hex string."""
    return _git(repo_root, "rev-parse", "HEAD").strip()


def get_tracked_info(repo_root: Path) -> tuple[frozenset[str], frozenset[str]]:
    """Return (regular_files, gitlinks) as POSIX-path frozensets.

    Regular files have git mode 100644 or 100755.
    Gitlinks (submodule entries) have mode 160000.
    Symlinks (mode 120000) are excluded from regular_files.
    """
    lines = _git(repo_root, "ls-files", "--stage").splitlines()
    regular: set[str] = set()
    gitlinks: set[str] = set()
    for line in lines:
        if not line:
            continue
        mode, rest = line.split(" ", 1)
        path = rest.split("\t", 1)[1]
        if mode in ("100644", "100755"):
            regular.add(path)
        elif mode == "160000":
            gitlinks.add(path)
    return frozenset(regular), frozenset(gitlinks)


def _git(repo_root: Path, *args: str) -> str:
    """Run a read-only git command and return stdout as a string."""
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={repo_root.as_posix()}",
            "-C",
            str(repo_root),
            *args,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout
