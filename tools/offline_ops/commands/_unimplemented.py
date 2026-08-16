"""Shared report builder for commands not yet implemented in this phase."""

from __future__ import annotations

from tools.offline_ops.exit_codes import ExitCode
from tools.offline_ops.models import CheckResult, CheckStatus, GateReport


def unimplemented_report(command: str, planned_phase: str) -> GateReport:
    """Build the ``GateReport`` for a command with no implementation yet.

    Args:
        command: CLI subcommand name, e.g. ``"quality-gate"``.
        planned_phase: Human-readable pointer to the workstream phase that
            will implement this command, for operator guidance.

    Returns:
        A ``GateReport`` with one ``CheckStatus.UNAVAILABLE`` check and an
        overall ``ExitCode.VALIDATOR_UNAVAILABLE`` exit code, per the
        Result contract in ``RELEASE_ENGINEERING_WORKSTREAM.md``.
    """
    check = CheckResult(
        check_id=command.replace("-", "_"),
        status=CheckStatus.UNAVAILABLE,
        explanation=f"{command} is not implemented yet; planned in {planned_phase}.",
        duration_seconds=0.0,
        exit_code=int(ExitCode.VALIDATOR_UNAVAILABLE),
    )
    return GateReport(
        command=command,
        checks=(check,),
        exit_code=int(ExitCode.VALIDATOR_UNAVAILABLE),
    )
