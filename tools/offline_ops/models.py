"""Typed result model shared by every offline-ops check and report renderer.

Every composed validator (pytest, Ruff, Hcommit vectors, the conformance
kit, match-artifact checks, secret scans, ...) must report through
``CheckResult``, and every command must return one ``GateReport``. Report
renderers (JSON, Markdown, CLI stdout) must render from these types only,
never from raw subprocess output, so that sensitive values never leak
into a generated report.
"""

from __future__ import annotations

import dataclasses
import enum


class CheckStatus(enum.Enum):
    """Sanitized outcome of one composed validator."""

    PASS = "pass"
    FAIL = "fail"
    SKIPPED = "skipped"
    UNAVAILABLE = "unavailable"


@dataclasses.dataclass(frozen=True)
class CheckResult:
    """One sanitized, immutable validator outcome.

    Attributes:
        check_id: Stable identifier for the validator, e.g. ``"pytest"`` or
            ``"hcommit_vectors"``. Stable across runs so reports can be
            diffed mechanically.
        status: Outcome of the validator, one of ``CheckStatus``.
        explanation: Sanitized, human-readable explanation. Must never
            contain raw stdout/stderr, secrets, nonces, or artifact bodies.
        duration_seconds: Wall-clock duration of the validator run.
        exit_code: The ``ExitCode`` value this check contributes to its
            command's overall exit code.
    """

    check_id: str
    status: CheckStatus
    explanation: str
    duration_seconds: float
    exit_code: int


@dataclasses.dataclass(frozen=True)
class GateReport:
    """Aggregate, immutable result of one CLI command invocation.

    Attributes:
        command: The CLI subcommand that produced this report, e.g.
            ``"quality-gate"``.
        checks: Ordered, sanitized individual check outcomes.
        exit_code: The single overall ``ExitCode`` for the invocation.
    """

    command: str
    checks: tuple[CheckResult, ...]
    exit_code: int
