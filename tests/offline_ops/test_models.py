"""CheckResult/GateReport must be immutable and carry sanitized fields."""

from __future__ import annotations

import dataclasses

import pytest

from tools.offline_ops.models import CheckResult, CheckStatus, GateReport


def _check(status: CheckStatus = CheckStatus.PASS) -> CheckResult:
    return CheckResult(
        check_id="pytest",
        status=status,
        explanation="all tests passed",
        duration_seconds=1.5,
        exit_code=0,
    )


def test_check_result_is_frozen() -> None:
    check = _check()
    with pytest.raises(dataclasses.FrozenInstanceError):
        check.status = CheckStatus.FAIL  # type: ignore[misc]


def test_gate_report_is_frozen() -> None:
    report = GateReport(command="quality-gate", checks=(_check(),), exit_code=0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        report.exit_code = 3  # type: ignore[misc]


def test_gate_report_preserves_check_order() -> None:
    ordered = (_check(CheckStatus.PASS), _check(CheckStatus.FAIL))
    report = GateReport(command="quality-gate", checks=ordered, exit_code=3)
    assert report.checks == ordered
