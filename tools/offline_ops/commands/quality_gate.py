"""``quality-gate`` command.

Composes existing local validators (never reimplements them) into one
aggregate report: project pytest, Ruff, the Hcommit golden vectors, the
frozen production-file manifest, the conformance kit, an optional match
artifact, and the repository secret scan.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from tools.offline_ops.checks.base import outcome_to_check
from tools.offline_ops.commands import scan_secrets, validate_match
from tools.offline_ops.exit_codes import ExitCode
from tools.offline_ops.models import CheckResult, CheckStatus, GateReport
from tools.offline_ops.subprocess_runner import CommandOutcome, run_command

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_TIMEOUT_SECONDS = 600.0

_SUBPROCESS_CHECKS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("pytest", ("uv", "run", "pytest")),
    ("ruff", ("uv", "run", "ruff", "check", "src", "tests")),
    (
        "hcommit_vectors",
        (
            "uv",
            "run",
            "pytest",
            "tests/test_phase4a_crypto_protocol.py::"
            "test_all_hcommit_golden_vectors_and_extra_fields",
            "--no-cov",
        ),
    ),
    (
        "frozen_manifest",
        (
            "uv",
            "run",
            "pytest",
            "tests/test_frozen_manifest.py::test_authoritative_seven_frozen_file_hashes",
            "--no-cov",
        ),
    ),
    (
        "conformance_kit",
        ("uv", "run", "python", "external/copthief-league-protocol/verify_vectors.py"),
    ),
)

#: This tool's own test suite necessarily contains synthetic secret-like
#: fixtures to exercise the scanner (see tests/offline_ops/test_secrets_
#: scanner.py); excluded here so quality-gate's repository-wide scan
#: never fails on its own known-safe test data. A direct ``scan-secrets``
#: invocation is unaffected and still scans exactly what it is given.
_SECRET_SCAN_EXCLUDE_RELATIVE_DIRS: frozenset[str] = frozenset({"tests/offline_ops"})

#: Priority order used to pick one overall exit code when several checks
#: fail with different documented codes: an unavailable validator always
#: wins (it can never be a PASS), then a secret-scan failure, then a match
#: validation failure, then a plain quality-check failure.
_FAILURE_PRIORITY: tuple[ExitCode, ...] = (
    ExitCode.VALIDATOR_UNAVAILABLE,
    ExitCode.SECRET_SCAN_FAILED,
    ExitCode.MATCH_VALIDATION_FAILED,
    ExitCode.QUALITY_CHECK_FAILED,
)


class CommandRunner(Protocol):
    """Callable shape of ``run_command``, injectable for deterministic tests."""

    def __call__(
        self, argv: Sequence[str], *, cwd: Path, timeout_seconds: float
    ) -> CommandOutcome: ...


def run(
    *,
    match_path: Path | None = None,
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
    repo_root: Path = _REPO_ROOT,
    scan_target: Path | None = None,
    command_runner: CommandRunner = run_command,
) -> GateReport:
    """Run the composed local quality gate and return its aggregate report.

    Args:
        match_path: Optional completed match artifact directory to
            validate as part of the gate; skipped when ``None``.
        timeout_seconds: Per-subprocess-check timeout.
        repo_root: Working directory for every composed subprocess check.
        scan_target: Directory scanned for secrets; defaults to
            ``repo_root``.
        command_runner: Subprocess execution strategy; overridable so
            tests never spawn a real, slow, recursive subprocess.

    Returns:
        One aggregate ``GateReport`` covering every composed check.
    """
    checks: list[CheckResult] = [
        outcome_to_check(
            check_id,
            command_runner(argv, cwd=repo_root, timeout_seconds=timeout_seconds),
            fail_exit_code=ExitCode.QUALITY_CHECK_FAILED,
        )
        for check_id, argv in _SUBPROCESS_CHECKS
    ]
    checks.append(_match_artifact_check(match_path))
    checks.append(_secret_scan_check(scan_target if scan_target is not None else repo_root))

    return GateReport(
        command="quality-gate", checks=tuple(checks), exit_code=_overall_exit_code(checks)
    )


def _secret_scan_check(scan_target: Path) -> CheckResult:
    report = scan_secrets.run(
        scan_target, exclude_relative_dirs=_SECRET_SCAN_EXCLUDE_RELATIVE_DIRS
    )
    return report.checks[0]


def _match_artifact_check(match_path: Path | None) -> CheckResult:
    if match_path is None:
        return CheckResult(
            check_id="match_artifact",
            status=CheckStatus.SKIPPED,
            explanation="no match path given; optional check skipped",
            duration_seconds=0.0,
            exit_code=int(ExitCode.SUCCESS),
        )
    result = validate_match.run(match_path).checks[0]
    return dataclasses.replace(result, check_id="match_artifact")


def _overall_exit_code(checks: Sequence[CheckResult]) -> int:
    blocking_statuses = (CheckStatus.FAIL, CheckStatus.UNAVAILABLE)
    blocking = {check.exit_code for check in checks if check.status in blocking_statuses}
    for code in _FAILURE_PRIORITY:
        if int(code) in blocking:
            return int(code)
    return int(ExitCode.SUCCESS)
