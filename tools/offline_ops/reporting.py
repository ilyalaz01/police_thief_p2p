"""Sanitized report rendering shared by every offline-ops command.

Phase 1 renders a single JSON form to stdout. Later phases may add an
equivalent Markdown report, but both must keep rendering exclusively from
``GateReport``/``CheckResult`` so no raw validator output can leak.
"""

from __future__ import annotations

import json

from tools.offline_ops.models import GateReport


def report_to_dict(report: GateReport) -> dict[str, object]:
    """Convert ``report`` into a plain, JSON-serializable dictionary."""
    return {
        "command": report.command,
        "exit_code": report.exit_code,
        "checks": [
            {
                "check_id": check.check_id,
                "status": check.status.value,
                "explanation": check.explanation,
                "duration_seconds": check.duration_seconds,
                "exit_code": check.exit_code,
            }
            for check in report.checks
        ],
    }


def render_report(report: GateReport) -> None:
    """Print a sanitized, deterministic JSON rendering of ``report``."""
    print(json.dumps(report_to_dict(report), indent=2, sort_keys=True))
