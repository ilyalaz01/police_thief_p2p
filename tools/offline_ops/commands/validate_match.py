"""``validate-match`` command.

Runs this tool's own filesystem-hygiene pass (unexpected/symlinked/
oversized/path-escaping files) first, then composes — never
reimplements — the existing MIT-licensed
``external/copthief-league-protocol/tools/check_artifacts.py`` checker for
schema 1.1 cross-artifact semantics.
"""

from __future__ import annotations

from pathlib import Path

from tools.offline_ops.checks.base import outcome_to_check
from tools.offline_ops.exit_codes import ExitCode
from tools.offline_ops.match_artifacts.hygiene import scan_artifact_directory
from tools.offline_ops.models import CheckResult, CheckStatus, GateReport
from tools.offline_ops.subprocess_runner import CommandRunner, run_command

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CHECKER = "external/copthief-league-protocol/tools/check_artifacts.py"
_DEFAULT_TIMEOUT_SECONDS = 60.0


def run(
    path: Path,
    *,
    repo_root: Path = _REPO_ROOT,
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
    command_runner: CommandRunner = run_command,
) -> GateReport:
    """Validate one match artifact directory and return its report.

    Args:
        path: Directory to validate.
        repo_root: Working directory for the composed checker subprocess.
        timeout_seconds: Timeout for the composed checker subprocess.
        command_runner: Subprocess execution strategy; overridable for tests.

    Returns:
        A two-check ``GateReport`` (``artifact_hygiene``,
        ``artifact_conformance``). The conformance check is skipped when
        hygiene fails, since an unsafe directory is never handed to the
        composed third-party checker.
    """
    resolved = path.resolve()
    try:
        findings = scan_artifact_directory(resolved)
    except FileNotFoundError:
        hygiene = _check(
            "artifact_hygiene",
            CheckStatus.FAIL,
            f"match directory does not exist: {path}",
            ExitCode.MATCH_VALIDATION_FAILED,
        )
        return _report((hygiene, _skipped_conformance()), hygiene.exit_code)

    if findings:
        categories = sorted({finding.category for finding in findings})
        hygiene = _check(
            "artifact_hygiene",
            CheckStatus.FAIL,
            f"{len(findings)} finding(s) across categories: {', '.join(categories)}",
            ExitCode.MATCH_VALIDATION_FAILED,
        )
        return _report((hygiene, _skipped_conformance()), hygiene.exit_code)

    hygiene = _check("artifact_hygiene", CheckStatus.PASS, "no findings", ExitCode.SUCCESS)
    outcome = command_runner(
        ("uv", "run", "python", _CHECKER, str(resolved), "--quiet"),
        cwd=repo_root,
        timeout_seconds=timeout_seconds,
    )
    conformance = outcome_to_check(
        "artifact_conformance", outcome, fail_exit_code=ExitCode.MATCH_VALIDATION_FAILED
    )
    return _report((hygiene, conformance), conformance.exit_code)


def _skipped_conformance() -> CheckResult:
    """Compute the internal skipped conformance step used by module."""
    return _check(
        "artifact_conformance",
        CheckStatus.SKIPPED,
        "artifact_hygiene failed; conformance check skipped",
        ExitCode.SUCCESS,
    )


def _check(
    check_id: str, status: CheckStatus, explanation: str, exit_code: ExitCode
) -> CheckResult:
    """Compute the internal check step used by module."""
    return CheckResult(
        check_id=check_id,
        status=status,
        explanation=explanation,
        duration_seconds=0.0,
        exit_code=int(exit_code),
    )


def _report(checks: tuple[CheckResult, ...], exit_code: int) -> GateReport:
    """Compute the internal report step used by module."""
    return GateReport(command="validate-match", checks=checks, exit_code=exit_code)
