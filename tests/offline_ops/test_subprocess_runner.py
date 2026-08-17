"""run_command must never raise; missing/timeout become sanitized outcomes."""

from __future__ import annotations

import sys
from pathlib import Path

from tools.offline_ops.subprocess_runner import run_command


def test_successful_command_reports_its_returncode(tmp_path: Path) -> None:
    outcome = run_command(
        [sys.executable, "-c", "import sys; sys.exit(0)"], cwd=tmp_path, timeout_seconds=30
    )
    assert outcome.returncode == 0
    assert not outcome.timed_out


def test_failing_command_reports_nonzero_returncode(tmp_path: Path) -> None:
    outcome = run_command(
        [sys.executable, "-c", "import sys; sys.exit(3)"], cwd=tmp_path, timeout_seconds=30
    )
    assert outcome.returncode == 3
    assert not outcome.timed_out


def test_missing_executable_is_reported_without_raising(tmp_path: Path) -> None:
    outcome = run_command(
        ["definitely-not-a-real-executable-xyz-12345"], cwd=tmp_path, timeout_seconds=30
    )
    assert outcome.returncode is None
    assert not outcome.timed_out


def test_slow_command_times_out_without_raising(tmp_path: Path) -> None:
    outcome = run_command(
        [sys.executable, "-c", "import time; time.sleep(5)"],
        cwd=tmp_path,
        timeout_seconds=0.05,
    )
    assert outcome.returncode is None
    assert outcome.timed_out


def test_paths_containing_spaces_are_passed_as_a_single_argument(tmp_path: Path) -> None:
    target = tmp_path / "dir with spaces"
    target.mkdir()
    script = "import sys; sys.exit(0 if len(sys.argv) == 2 else 1)"
    outcome = run_command(
        [sys.executable, "-c", script, str(target)], cwd=tmp_path, timeout_seconds=30
    )
    assert outcome.returncode == 0
