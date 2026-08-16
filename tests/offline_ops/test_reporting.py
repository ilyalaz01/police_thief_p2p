"""render_report must render only sanitized GateReport/CheckResult fields."""

from __future__ import annotations

import json

import pytest

from tools.offline_ops.models import CheckResult, CheckStatus, GateReport
from tools.offline_ops.reporting import render_report, report_to_dict


@pytest.fixture
def report() -> GateReport:
    check = CheckResult(
        check_id="ruff",
        status=CheckStatus.PASS,
        explanation="zero violations",
        duration_seconds=0.25,
        exit_code=0,
    )
    return GateReport(command="quality-gate", checks=(check,), exit_code=0)


def test_report_to_dict_contains_only_sanitized_fields(report: GateReport) -> None:
    payload = report_to_dict(report)
    assert payload == {
        "command": "quality-gate",
        "exit_code": 0,
        "checks": [
            {
                "check_id": "ruff",
                "status": "pass",
                "explanation": "zero violations",
                "duration_seconds": 0.25,
                "exit_code": 0,
            }
        ],
    }


def test_render_report_prints_valid_json(
    report: GateReport, capsys: pytest.CaptureFixture[str]
) -> None:
    render_report(report)
    printed = json.loads(capsys.readouterr().out)
    assert printed == report_to_dict(report)
