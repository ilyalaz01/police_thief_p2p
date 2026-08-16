"""Turn one sanitized ``CommandOutcome`` into a sanitized ``CheckResult``.

A missing, skipped, timed-out, or unrunnable required validator must never
be reported as a PASS; both timeout and missing-executable outcomes are
mapped to ``CheckStatus.UNAVAILABLE`` here.
"""

from __future__ import annotations

from tools.offline_ops.exit_codes import ExitCode
from tools.offline_ops.models import CheckResult, CheckStatus
from tools.offline_ops.subprocess_runner import CommandOutcome


def outcome_to_check(
    check_id: str, outcome: CommandOutcome, *, fail_exit_code: ExitCode
) -> CheckResult:
    """Interpret ``outcome`` as a sanitized ``CheckResult`` for ``check_id``.

    Args:
        check_id: Stable identifier for the validator, e.g. ``"pytest"``.
        outcome: Raw subprocess outcome to interpret.
        fail_exit_code: The ``ExitCode`` to use when the validator ran but
            reported failure (non-zero exit).

    Returns:
        A sanitized ``CheckResult``. Never includes raw stdout/stderr.
    """
    if outcome.timed_out:
        return CheckResult(
            check_id=check_id,
            status=CheckStatus.UNAVAILABLE,
            explanation=f"{check_id} timed out",
            duration_seconds=outcome.duration_seconds,
            exit_code=int(ExitCode.VALIDATOR_UNAVAILABLE),
        )
    if outcome.returncode is None:
        return CheckResult(
            check_id=check_id,
            status=CheckStatus.UNAVAILABLE,
            explanation=f"{check_id} dependency is unavailable",
            duration_seconds=outcome.duration_seconds,
            exit_code=int(ExitCode.VALIDATOR_UNAVAILABLE),
        )
    if outcome.returncode == 0:
        return CheckResult(
            check_id=check_id,
            status=CheckStatus.PASS,
            explanation=f"{check_id} passed",
            duration_seconds=outcome.duration_seconds,
            exit_code=int(ExitCode.SUCCESS),
        )
    return CheckResult(
        check_id=check_id,
        status=CheckStatus.FAIL,
        explanation=f"{check_id} failed (exit code {outcome.returncode})",
        duration_seconds=outcome.duration_seconds,
        exit_code=int(fail_exit_code),
    )
