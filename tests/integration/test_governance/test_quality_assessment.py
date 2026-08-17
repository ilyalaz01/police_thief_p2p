"""Governance tests for the reproducible quality-assessment package."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tests.support.project_paths import PROJECT_ROOT  # noqa: E402
from tools.quality_assessment import measure  # noqa: E402  # RED: absent until feat commit

ROOT = PROJECT_ROOT
ISO_DOC = ROOT / "docs/ISO_IEC_25010_ASSESSMENT.md"
COST_DOC = ROOT / "docs/COST_AND_CAPACITY_ANALYSIS.md"
QA_TOOLS_DIR = ROOT / "tools/quality_assessment"

ISO_CHARACTERISTICS = [
    "Functional suitability",
    "Performance efficiency",
    "Compatibility",
    "Usability",
    "Reliability",
    "Security",
    "Maintainability",
    "Portability",
]


def test_measure_deterministic_output() -> None:
    """Same repo root produces identical output on repeated calls."""
    first = measure.measure_repository(ROOT)
    second = measure.measure_repository(ROOT)
    assert first == second


def test_untracked_ignored_content_excluded() -> None:
    """Git-untracked and ignored directories never appear in tracked file output."""
    data = measure.measure_repository(ROOT)
    for entry in data["largest_files_by_bytes"]:
        path = entry["path"]
        assert not path.startswith(".git/"), path
        assert "__pycache__" not in path, path
        assert ".venv" not in path, path
    assert data["tracked_file_count"] > 0


def test_paths_are_relative_no_absolute_root() -> None:
    """Output paths are repository-relative POSIX strings without the absolute root."""
    root_str = str(ROOT)
    data = measure.measure_repository(ROOT)
    for entry in data["largest_files_by_bytes"]:
        path = entry["path"]
        assert root_str not in path, f"absolute root leaked into path: {path}"
        assert not path.startswith("/"), path
        assert ":\\" not in path, path


def test_stable_ordering_across_runs() -> None:
    """JSON serialisation of two consecutive runs is byte-identical."""
    run_a = json.dumps(measure.measure_repository(ROOT), sort_keys=True)
    run_b = json.dumps(measure.measure_repository(ROOT), sort_keys=True)
    assert run_a == run_b


def test_invalid_repository_refused() -> None:
    """A directory without .git causes SystemExit with a non-zero code."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(SystemExit) as exc_info:
            measure.measure_repository(Path(tmpdir))
        assert exc_info.value.code != 0


def test_cost_doc_required_limitations() -> None:
    """Cost and capacity document contains all required limitation statements."""
    text = COST_DOC.read_text(encoding="utf-8")
    required = [
        "$0 observed",
        "T_in",
        "T_out",
        "P_in",
        "P_out",
        "unmeasured",
        "observed",
    ]
    for phrase in required:
        assert phrase in text, f"cost doc missing required phrase: {phrase!r}"


def test_iso_doc_all_eight_characteristics() -> None:
    """ISO/IEC 25010 document covers all eight product-quality characteristics."""
    text = ISO_DOC.read_text(encoding="utf-8")
    assert "Internal engineering assessment" in text
    assert "not an ISO certification" in text
    for char in ISO_CHARACTERISTICS:
        assert char in text, f"ISO doc missing characteristic: {char!r}"


def test_new_python_files_within_150_lines() -> None:
    """Every Python file added under tools/quality_assessment/ obeys the 150-line rule."""
    violations: dict[str, int] = {}
    for path in QA_TOOLS_DIR.rglob("*.py"):
        counted = sum(
            bool(line.strip()) and not line.lstrip().startswith("#")
            for line in path.read_text(encoding="utf-8").splitlines()
        )
        if counted > 150:
            violations[path.relative_to(ROOT).as_posix()] = counted
    assert violations == {}
