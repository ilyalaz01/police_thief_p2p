"""CLI dispatch must honor the documented exit-code contract.

``quality-gate`` is deliberately never invoked end-to-end here: it shells
out to a real, slow, recursive ``uv run pytest``. Its dispatch/aggregation
logic is covered in isolation in ``test_quality_gate.py`` with an injected
command runner instead. ``validate-match``/``package-match`` compose a
fast, stdlib-only, non-recursive checker, so they are exercised for real.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.offline_ops.artifact_fixtures import write_valid_match_fixture
from tools.offline_ops.cli import build_parser, main
from tools.offline_ops.exit_codes import ExitCode


def test_help_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--help"]) == ExitCode.SUCCESS
    assert "offline-ops" in capsys.readouterr().out


def test_no_subcommand_is_invalid_invocation() -> None:
    assert main([]) == ExitCode.INVALID_INVOCATION


def test_unknown_subcommand_is_invalid_invocation() -> None:
    assert main(["not-a-real-command"]) == ExitCode.INVALID_INVOCATION


def test_validate_match_missing_path_is_invalid_invocation() -> None:
    assert main(["validate-match"]) == ExitCode.INVALID_INVOCATION


def test_package_match_missing_output_is_invalid_invocation() -> None:
    assert main(["package-match", "some/path"]) == ExitCode.INVALID_INVOCATION


def test_quality_gate_flags_parse_without_executing_anything() -> None:
    args = build_parser().parse_args(["quality-gate", "--match-path", "x", "--timeout", "5"])
    assert args.match_path == Path("x")
    assert args.timeout == 5.0


def test_validate_match_passes_on_a_valid_fixture(tmp_path: Path) -> None:
    write_valid_match_fixture(tmp_path)
    assert main(["validate-match", str(tmp_path)]) == ExitCode.SUCCESS


def test_package_match_writes_a_package_for_a_valid_fixture(tmp_path: Path) -> None:
    source = tmp_path / "source"
    write_valid_match_fixture(source)
    output = tmp_path / "package"

    assert main(["package-match", str(source), "--output", str(output)]) == ExitCode.SUCCESS
    assert (output / "package_manifest.json").exists()


def test_scan_secrets_passes_on_an_empty_directory(tmp_path: Path) -> None:
    assert main(["scan-secrets", str(tmp_path)]) == ExitCode.SUCCESS


def test_paths_containing_spaces_are_accepted(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["validate-match", "dir with spaces/match one"])
    assert exit_code == ExitCode.MATCH_VALIDATION_FAILED
    payload = json.loads(capsys.readouterr().out)
    assert payload["command"] == "validate-match"


def test_report_is_rendered_as_sanitized_json(capsys: pytest.CaptureFixture[str]) -> None:
    main(["package-match", "some/nonexistent/path", "--output", "some/out"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["command"] == "package-match"
    assert payload["exit_code"] == ExitCode.MATCH_VALIDATION_FAILED
    assert payload["checks"][0]["status"] == "fail"
