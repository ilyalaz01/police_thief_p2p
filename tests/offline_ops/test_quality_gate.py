"""quality-gate must compose checks and pick the correct overall exit code.

The five composed subprocess checks are faked here via ``command_runner``:
one of them shells out to a full recursive ``uv run pytest``, which must
never run inside this suite's own test run. ``match_path`` is exercised
for real instead: it composes validate-match's fast, non-recursive,
stdlib-only checker, so a genuine subprocess call there is safe.
"""

from __future__ import annotations

from pathlib import Path

from tests.offline_ops.artifact_fixtures import write_valid_match_fixture
from tools.offline_ops.commands import quality_gate
from tools.offline_ops.exit_codes import ExitCode
from tools.offline_ops.models import CheckStatus
from tools.offline_ops.subprocess_runner import CommandOutcome

_PASS = CommandOutcome(returncode=0, timed_out=False, duration_seconds=0.01)
_FAIL = CommandOutcome(returncode=1, timed_out=False, duration_seconds=0.01)
_MISSING = CommandOutcome(returncode=None, timed_out=False, duration_seconds=0.0)


def _make_runner(overrides: dict[str, CommandOutcome]):
    def runner(argv, *, cwd: Path, timeout_seconds: float) -> CommandOutcome:
        joined = " ".join(argv).lower()
        if tuple(argv) == ("uv", "run", "pytest"):
            return overrides.get("pytest", _PASS)
        if "ruff" in joined:
            return overrides.get("ruff", _PASS)
        if "hcommit" in joined:
            return overrides.get("hcommit_vectors", _PASS)
        if "frozen" in joined:
            return overrides.get("frozen_manifest", _PASS)
        if "verify_vectors" in joined:
            return overrides.get("conformance_kit", _PASS)
        raise AssertionError(f"unexpected argv in test: {argv!r}")

    return runner


def test_all_checks_passing_yields_success(tmp_path: Path) -> None:
    report = quality_gate.run(
        repo_root=tmp_path, scan_target=tmp_path, command_runner=_make_runner({})
    )
    assert report.exit_code == ExitCode.SUCCESS
    assert {check.check_id for check in report.checks} == {
        "pytest",
        "ruff",
        "hcommit_vectors",
        "frozen_manifest",
        "conformance_kit",
        "match_artifact",
        "scan_secrets",
    }
    match_artifact = next(c for c in report.checks if c.check_id == "match_artifact")
    assert match_artifact.status == CheckStatus.SKIPPED


def test_a_failing_quality_check_yields_quality_check_failed(tmp_path: Path) -> None:
    report = quality_gate.run(
        repo_root=tmp_path,
        scan_target=tmp_path,
        command_runner=_make_runner({"ruff": _FAIL}),
    )
    assert report.exit_code == ExitCode.QUALITY_CHECK_FAILED


def test_a_missing_dependency_outranks_a_quality_check_failure(tmp_path: Path) -> None:
    report = quality_gate.run(
        repo_root=tmp_path,
        scan_target=tmp_path,
        command_runner=_make_runner({"ruff": _FAIL, "conformance_kit": _MISSING}),
    )
    assert report.exit_code == ExitCode.VALIDATOR_UNAVAILABLE


def test_secret_scan_failure_outranks_a_quality_check_failure(tmp_path: Path) -> None:
    (tmp_path / "leaked.txt").write_text(
        "-----BEGIN RSA PRIVATE KEY-----\nFAKE\n-----END RSA PRIVATE KEY-----\n",
        encoding="utf-8",
    )
    report = quality_gate.run(
        repo_root=tmp_path,
        scan_target=tmp_path,
        command_runner=_make_runner({"ruff": _FAIL}),
    )
    assert report.exit_code == ExitCode.SECRET_SCAN_FAILED


def test_default_scan_target_excludes_this_tools_own_test_fixtures(tmp_path: Path) -> None:
    own_tests = tmp_path / "tests" / "offline_ops"
    own_tests.mkdir(parents=True)
    (own_tests / "fixture.txt").write_text("AKIAAAAAAAAAAAAAAAAA", encoding="utf-8")

    report = quality_gate.run(repo_root=tmp_path, command_runner=_make_runner({}))

    assert report.exit_code == ExitCode.SUCCESS


def test_a_secret_outside_the_excluded_test_directory_still_fails(tmp_path: Path) -> None:
    (tmp_path / "leaked.txt").write_text("AKIAAAAAAAAAAAAAAAAA", encoding="utf-8")

    report = quality_gate.run(repo_root=tmp_path, command_runner=_make_runner({}))

    assert report.exit_code == ExitCode.SECRET_SCAN_FAILED


def test_an_invalid_match_path_is_reported_and_fails_the_gate(tmp_path: Path) -> None:
    empty_match_dir = tmp_path / "match"
    empty_match_dir.mkdir()
    report = quality_gate.run(
        match_path=empty_match_dir,
        repo_root=tmp_path,
        scan_target=tmp_path,
        command_runner=_make_runner({}),
    )
    match_artifact = next(c for c in report.checks if c.check_id == "match_artifact")
    assert match_artifact.status == CheckStatus.FAIL
    assert report.exit_code == ExitCode.MATCH_VALIDATION_FAILED


def test_a_valid_match_path_passes_the_gate(tmp_path: Path) -> None:
    match_dir = tmp_path / "match"
    write_valid_match_fixture(match_dir)
    report = quality_gate.run(
        match_path=match_dir,
        repo_root=tmp_path,
        scan_target=tmp_path,
        command_runner=_make_runner({}),
    )
    match_artifact = next(c for c in report.checks if c.check_id == "match_artifact")
    assert match_artifact.status == CheckStatus.PASS
    assert report.exit_code == ExitCode.SUCCESS
