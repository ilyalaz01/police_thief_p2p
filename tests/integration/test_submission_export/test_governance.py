"""Governance: all submission_export Python files obey the 150-line rule."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

_ROOT = Path(__file__).resolve().parents[3]
_DIRS = [
    _ROOT / "tools/submission_export",
    _ROOT / "tests/integration/test_submission_export",
]


def _count_lines(path: Path) -> int:
    return sum(
        bool(line.strip()) and not line.lstrip().startswith("#")
        for line in path.read_text(encoding="utf-8").splitlines()
    )


def test_all_new_python_files_within_150_lines() -> None:
    violations: dict[str, int] = {}
    for directory in _DIRS:
        for path in directory.rglob("*.py"):
            counted = _count_lines(path)
            if counted > 150:
                violations[path.relative_to(_ROOT).as_posix()] = counted
    assert violations == {}
