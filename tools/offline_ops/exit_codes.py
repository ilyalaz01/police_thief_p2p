"""Stable process exit codes for the offline-ops CLI.

Values and meanings are fixed by the "Result contract" table in
``docs/RELEASE_ENGINEERING_WORKSTREAM.md``. Code ``1`` is intentionally
unassigned in that contract and is reserved for uncaught interpreter
failures; it must never be assigned to a documented outcome here.
"""

from __future__ import annotations

import enum


class ExitCode(enum.IntEnum):
    """Overall or per-check exit code returned by the offline-ops CLI."""

    SUCCESS = 0
    INVALID_INVOCATION = 2
    QUALITY_CHECK_FAILED = 3
    SECRET_SCAN_FAILED = 4
    MATCH_VALIDATION_FAILED = 5
    VALIDATOR_UNAVAILABLE = 6
    OUTPUT_WRITE_FAILED = 7
