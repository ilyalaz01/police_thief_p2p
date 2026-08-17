"""``scan-secrets`` command.

Fail-closed filesystem scan for credentials, tokens, private keys, tunnel
configuration, caches/temp files, symlinks, path traversal, and
non-artifact nonce material. Findings never retain matched text.
"""

from __future__ import annotations

import time
from pathlib import Path

from tools.offline_ops.exit_codes import ExitCode
from tools.offline_ops.models import CheckResult, CheckStatus, GateReport
from tools.offline_ops.secrets.scanner import scan_path


def run(path: Path, *, exclude_relative_dirs: frozenset[str] = frozenset()) -> GateReport:
    """Scan ``path`` and return a sanitized secret-scan report.

    Args:
        path: Directory to scan for fail-closed findings.
        exclude_relative_dirs: Forwarded to ``scan_path``; see its
            docstring. Empty for a direct CLI invocation, which always
            scans exactly what the operator asked for.

    Returns:
        A single-check ``GateReport``. ``PASS`` with exit 0 if no findings,
        ``FAIL`` with exit 4 if any finding exists, or ``UNAVAILABLE`` with
        exit 6 if ``path`` does not exist.
    """
    start = time.monotonic()
    try:
        findings = scan_path(path, exclude_relative_dirs=exclude_relative_dirs)
    except FileNotFoundError:
        return _report(
            status=CheckStatus.UNAVAILABLE,
            explanation=f"scan target does not exist: {path}",
            exit_code=ExitCode.VALIDATOR_UNAVAILABLE,
            duration_seconds=time.monotonic() - start,
        )

    duration = time.monotonic() - start
    if findings:
        categories = sorted({finding.category for finding in findings})
        return _report(
            status=CheckStatus.FAIL,
            explanation=f"{len(findings)} finding(s) across categories: {', '.join(categories)}",
            exit_code=ExitCode.SECRET_SCAN_FAILED,
            duration_seconds=duration,
        )
    return _report(
        status=CheckStatus.PASS,
        explanation="no findings",
        exit_code=ExitCode.SUCCESS,
        duration_seconds=duration,
    )


def _report(
    *, status: CheckStatus, explanation: str, exit_code: ExitCode, duration_seconds: float
) -> GateReport:
    check = CheckResult(
        check_id="scan_secrets",
        status=status,
        explanation=explanation,
        duration_seconds=duration_seconds,
        exit_code=int(exit_code),
    )
    return GateReport(command="scan-secrets", checks=(check,), exit_code=check.exit_code)
