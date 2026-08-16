"""``package-match`` command.

Validates first via ``validate-match``, then atomically packages the
validated directory: the original artifact files byte-for-byte unchanged,
plus one redacted JSON manifest and one equivalent redacted Markdown
report. An existing output path is never overwritten.
"""

from __future__ import annotations

from pathlib import Path

from tools.offline_ops.commands import validate_match
from tools.offline_ops.exit_codes import ExitCode
from tools.offline_ops.match_artifacts.packager import (
    build_manifest,
    render_markdown,
    write_package,
)
from tools.offline_ops.models import CheckResult, CheckStatus, GateReport
from tools.offline_ops.subprocess_runner import CommandRunner, run_command

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_TIMEOUT_SECONDS = 60.0


def run(
    path: Path,
    output: Path,
    *,
    repo_root: Path = _REPO_ROOT,
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
    command_runner: CommandRunner = run_command,
) -> GateReport:
    """Validate ``path``, then atomically package it into ``output``.

    Returns:
        A report combining validate-match's checks with one
        ``package_write`` check. Nothing is written if validation fails
        or if ``output`` already exists.
    """
    validation = validate_match.run(
        path, repo_root=repo_root, timeout_seconds=timeout_seconds, command_runner=command_runner
    )
    if validation.exit_code != int(ExitCode.SUCCESS):
        return GateReport(
            command="package-match", checks=validation.checks, exit_code=validation.exit_code
        )

    resolved_output = output.resolve()
    if resolved_output.exists():
        write_check = _write_check(
            CheckStatus.FAIL,
            f"output path already exists and will not be overwritten: {output}",
            ExitCode.OUTPUT_WRITE_FAILED,
        )
        return _report(validation, write_check)

    artifact_files = sorted(entry for entry in path.resolve().iterdir() if entry.is_file())
    manifest = build_manifest(artifact_files, validation)
    markdown = render_markdown(manifest)
    try:
        write_package(artifact_files, manifest, markdown, resolved_output)
    except OSError as exc:
        write_check = _write_check(
            CheckStatus.FAIL, f"package write failed: {exc}", ExitCode.OUTPUT_WRITE_FAILED
        )
        return _report(validation, write_check)

    write_check = _write_check(CheckStatus.PASS, f"package written to {output}", ExitCode.SUCCESS)
    return _report(validation, write_check)


def _write_check(status: CheckStatus, explanation: str, exit_code: ExitCode) -> CheckResult:
    return CheckResult(
        check_id="package_write",
        status=status,
        explanation=explanation,
        duration_seconds=0.0,
        exit_code=int(exit_code),
    )


def _report(validation: GateReport, write_check: CheckResult) -> GateReport:
    return GateReport(
        command="package-match",
        checks=(*validation.checks, write_check),
        exit_code=write_check.exit_code,
    )
