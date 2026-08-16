"""validate-match must compose the real MIT checker and fail closed.

Real end-to-end subprocess calls are used here (unlike quality-gate's
``pytest`` composition): the composed checker is fast, stdlib-only, and
never recursively invokes this test suite, so exercising it for real is
both safe and gives genuine confidence in the argv/exit-code wiring.
"""

from __future__ import annotations

from pathlib import Path

from tests.offline_ops.artifact_fixtures import write_valid_match_fixture
from tools.offline_ops.commands import validate_match
from tools.offline_ops.exit_codes import ExitCode
from tools.offline_ops.models import CheckStatus
from tools.offline_ops.subprocess_runner import CommandOutcome


def test_valid_fixture_passes_end_to_end(tmp_path: Path) -> None:
    write_valid_match_fixture(tmp_path)

    report = validate_match.run(tmp_path)

    assert report.exit_code == ExitCode.SUCCESS
    assert {c.check_id: c.status for c in report.checks} == {
        "artifact_hygiene": CheckStatus.PASS,
        "artifact_conformance": CheckStatus.PASS,
    }


def test_missing_directory_is_match_validation_failed(tmp_path: Path) -> None:
    report = validate_match.run(tmp_path / "does-not-exist")

    assert report.exit_code == ExitCode.MATCH_VALIDATION_FAILED
    hygiene, conformance = report.checks
    assert hygiene.status == CheckStatus.FAIL
    assert conformance.status == CheckStatus.SKIPPED


def test_unexpected_file_fails_hygiene_and_never_invokes_the_checker(tmp_path: Path) -> None:
    write_valid_match_fixture(tmp_path)
    (tmp_path / "debug_notes.txt").write_text("not an artifact", encoding="utf-8")

    def _must_not_be_called(argv, *, cwd, timeout_seconds):
        raise AssertionError("conformance checker must be skipped when hygiene fails")

    report = validate_match.run(tmp_path, command_runner=_must_not_be_called)

    assert report.exit_code == ExitCode.MATCH_VALIDATION_FAILED
    hygiene, conformance = report.checks
    assert hygiene.status == CheckStatus.FAIL
    assert conformance.status == CheckStatus.SKIPPED


def test_malformed_json_fails_via_the_composed_checker(tmp_path: Path) -> None:
    write_valid_match_fixture(tmp_path)
    declaration = next(tmp_path.glob("declaration_*.json"))
    declaration.write_text("{not valid json", encoding="utf-8")

    report = validate_match.run(tmp_path)

    assert report.exit_code == ExitCode.MATCH_VALIDATION_FAILED
    hygiene, conformance = report.checks
    assert hygiene.status == CheckStatus.PASS
    assert conformance.status == CheckStatus.FAIL


def test_a_missing_conformance_dependency_is_validator_unavailable(tmp_path: Path) -> None:
    write_valid_match_fixture(tmp_path)
    missing = CommandOutcome(returncode=None, timed_out=False, duration_seconds=0.0)

    report = validate_match.run(tmp_path, command_runner=lambda *a, **k: missing)

    assert report.exit_code == ExitCode.VALIDATOR_UNAVAILABLE


def test_a_conformance_timeout_is_validator_unavailable(tmp_path: Path) -> None:
    write_valid_match_fixture(tmp_path)
    timed_out = CommandOutcome(returncode=None, timed_out=True, duration_seconds=5.0)

    report = validate_match.run(tmp_path, command_runner=lambda *a, **k: timed_out)

    assert report.exit_code == ExitCode.VALIDATOR_UNAVAILABLE


def test_checker_invocation_uses_an_argument_array_never_a_shell_string(tmp_path: Path) -> None:
    write_valid_match_fixture(tmp_path)
    captured: dict[str, object] = {}

    def _capture(argv, *, cwd, timeout_seconds):
        captured["argv"] = tuple(argv)
        captured["cwd"] = cwd
        return CommandOutcome(returncode=0, timed_out=False, duration_seconds=0.01)

    validate_match.run(tmp_path, command_runner=_capture)

    argv = captured["argv"]
    assert isinstance(argv, tuple) and all(isinstance(part, str) for part in argv)
    assert argv[-2:] == (str(tmp_path.resolve()), "--quiet")
    assert argv[0:3] == ("uv", "run", "python")
