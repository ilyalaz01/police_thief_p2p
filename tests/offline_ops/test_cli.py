"""CLI dispatch must honor the documented exit-code contract."""

from __future__ import annotations

import json

import pytest

from tools.offline_ops.cli import main
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


@pytest.mark.parametrize(
    "argv",
    [
        ["quality-gate"],
        ["validate-match", "some/match/dir"],
        ["package-match", "some/match/dir", "--output", "some/out/dir"],
        ["scan-secrets", "some/match/dir"],
    ],
)
def test_unimplemented_commands_return_validator_unavailable(argv: list[str]) -> None:
    assert main(argv) == ExitCode.VALIDATOR_UNAVAILABLE


def test_paths_containing_spaces_are_accepted(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["validate-match", "dir with spaces/match one"])
    assert exit_code == ExitCode.VALIDATOR_UNAVAILABLE
    payload = json.loads(capsys.readouterr().out)
    assert payload["command"] == "validate-match"


def test_report_is_rendered_as_sanitized_json(capsys: pytest.CaptureFixture[str]) -> None:
    main(["quality-gate"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["command"] == "quality-gate"
    assert payload["exit_code"] == ExitCode.VALIDATOR_UNAVAILABLE
    assert payload["checks"][0]["status"] == "unavailable"
