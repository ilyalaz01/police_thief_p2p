"""outcome_to_check must never report an unavailable/timed-out run as PASS."""

from __future__ import annotations

from tools.offline_ops.checks.base import outcome_to_check
from tools.offline_ops.exit_codes import ExitCode
from tools.offline_ops.models import CheckStatus
from tools.offline_ops.subprocess_runner import CommandOutcome


def test_zero_returncode_is_pass() -> None:
    outcome = CommandOutcome(returncode=0, timed_out=False, duration_seconds=1.0)
    check = outcome_to_check("pytest", outcome, fail_exit_code=ExitCode.QUALITY_CHECK_FAILED)
    assert check.status == CheckStatus.PASS
    assert check.exit_code == ExitCode.SUCCESS


def test_nonzero_returncode_uses_the_given_fail_exit_code() -> None:
    outcome = CommandOutcome(returncode=1, timed_out=False, duration_seconds=1.0)
    check = outcome_to_check("ruff", outcome, fail_exit_code=ExitCode.QUALITY_CHECK_FAILED)
    assert check.status == CheckStatus.FAIL
    assert check.exit_code == ExitCode.QUALITY_CHECK_FAILED


def test_timeout_is_unavailable_never_pass() -> None:
    outcome = CommandOutcome(returncode=None, timed_out=True, duration_seconds=30.0)
    check = outcome_to_check("pytest", outcome, fail_exit_code=ExitCode.QUALITY_CHECK_FAILED)
    assert check.status == CheckStatus.UNAVAILABLE
    assert check.exit_code == ExitCode.VALIDATOR_UNAVAILABLE


def test_missing_dependency_is_unavailable_never_pass() -> None:
    outcome = CommandOutcome(returncode=None, timed_out=False, duration_seconds=0.0)
    check = outcome_to_check(
        "conformance_kit", outcome, fail_exit_code=ExitCode.QUALITY_CHECK_FAILED
    )
    assert check.status == CheckStatus.UNAVAILABLE
    assert check.exit_code == ExitCode.VALIDATOR_UNAVAILABLE
