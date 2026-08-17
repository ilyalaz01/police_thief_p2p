"""Deterministic repository quality measurement tool.

Inspects only Git-tracked files via ``git ls-files``. Produces stable
JSON on stdout with UTF-8 encoding and sorted keys. Never emits absolute
paths, usernames, credentials, or file contents.

Usage:
    python tools/quality_assessment/measure.py --repo-root .
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_AREAS: dict[str, str] = {
    "src": "src/",
    "tests": "tests/",
    "tools": "tools/",
    "docs": "docs/",
    "interop": "interop/",
    "config": "config/",
    "reports": "reports/",
    "external": "external/",
    "other": "",
}
_AREA_ORDER = list(_AREAS)


def _require_git_worktree(root: Path) -> None:
    """Exit with a clear message when root is not a Git worktree."""
    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.exit("error: repository root is not a Git worktree")


def _tracked_files(root: Path) -> list[str]:
    """Return sorted repository-relative POSIX paths for all tracked files."""
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.exit("error: unable to enumerate tracked files")
    return sorted(p for p in result.stdout.split("\0") if p)


def _classify(path: str) -> str:
    """Return the area key for a repository-relative POSIX path."""
    for area, prefix in _AREAS.items():
        if area != "other" and path.startswith(prefix):
            return area
    return "other"


def _nonblank_noncomment(root: Path, rel: str) -> int:
    """Count nonblank non-comment lines in a Python source file."""
    entry = root / rel
    if entry.is_symlink() or not entry.is_file():
        return 0
    try:
        lines = entry.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return 0
    return sum(bool(ln.strip()) and not ln.lstrip().startswith("#") for ln in lines)


def _count_test_fns(root: Path, rel: str) -> int:
    """Count ``def test_`` function definitions in a tracked Python file."""
    entry = root / rel
    if entry.is_symlink() or not entry.is_file():
        return 0
    try:
        text = entry.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    return sum(1 for ln in text.splitlines() if ln.lstrip().startswith("def test_"))


def measure_repository(root: Path, timestamp: str | None = None, top_n: int = 10) -> dict:
    """Return a deterministic quality-measurement mapping for a Git worktree.

    Args:
        root: Absolute path to the repository root; must be a Git worktree.
        timestamp: Optional ISO-8601 string. Omit to keep output byte-identical
            across repeated runs on the same commit.
        top_n: Number of largest tracked files to include in the output.
    """
    _require_git_worktree(root)
    tracked = _tracked_files(root)

    area_stats: dict[str, dict] = {a: {"file_count": 0, "byte_total": 0} for a in _AREA_ORDER}
    py_src_files = py_test_files = py_src_lines = py_test_lines = test_fn_count = 0
    sizes: list[tuple[int, str]] = []

    for rel in tracked:
        entry = root / rel
        try:
            size = entry.stat().st_size if entry.is_file() and not entry.is_symlink() else 0
        except OSError:
            size = 0
        area = _classify(rel)
        area_stats[area]["file_count"] += 1
        area_stats[area]["byte_total"] += size
        sizes.append((size, rel))
        if rel.endswith(".py"):
            nc = _nonblank_noncomment(root, rel)
            in_src = rel.startswith("src/")
            in_test = rel.startswith("tests/")
            if in_src:
                py_src_files += 1
                py_src_lines += nc
            if in_test:
                py_test_files += 1
                py_test_lines += nc
                test_fn_count += _count_test_fns(root, rel)

    sizes.sort(key=lambda t: (-t[0], t[1]))
    result: dict = {
        "schema": "quality_assessment_v1",
        "tracked_file_count": len(tracked),
        "tracked_byte_total": sum(s for s, _ in sizes),
        "areas": area_stats,
        "python": {
            "source_file_count": py_src_files,
            "test_file_count": py_test_files,
            "source_nonblank_noncomment_lines": py_src_lines,
            "test_nonblank_noncomment_lines": py_test_lines,
        },
        "test_function_count": {
            "method": "counted_def_test_in_tracked_py_files",
            "count": test_fn_count,
        },
        "largest_files_by_bytes": [
            {"path": rel, "bytes": sz} for sz, rel in sizes[:top_n]
        ],
    }
    if timestamp is not None:
        result["timestamp"] = timestamp
    return result


def main(argv: list[str] | None = None) -> None:
    """CLI entry point: print a deterministic JSON measurement to stdout."""
    parser = argparse.ArgumentParser(
        description="Measure Git-tracked repository files deterministically."
    )
    parser.add_argument("--repo-root", required=True,
                        help="Path to the repository root (must be a Git worktree).")
    parser.add_argument("--timestamp",
                        help="Optional ISO-8601 timestamp; omit for reproducible output.")
    parser.add_argument("--top", type=int, default=10,
                        help="Number of largest files to list (default: 10).")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    if not root.is_dir():
        sys.exit("error: repository root is not a directory")
    data = measure_repository(root, timestamp=args.timestamp, top_n=args.top)
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
