"""Argument-array subprocess execution shared by every composed validator.

Every invocation uses a ``Sequence[str]`` argument array, never a shell
string, and never touches the network. Raw stdout/stderr is intentionally
discarded after execution so it can never leak into a generated report.
"""

from __future__ import annotations

import dataclasses
import subprocess
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol


@dataclasses.dataclass(frozen=True)
class CommandOutcome:
    """Sanitized outcome of one subprocess invocation.

    Attributes:
        returncode: Process exit code, or ``None`` if the process never
            produced one (timeout or missing executable/dependency).
        timed_out: Whether the invocation exceeded ``timeout_seconds``.
        duration_seconds: Wall-clock duration of the invocation attempt.
    """

    returncode: int | None
    timed_out: bool
    duration_seconds: float


class CommandRunner(Protocol):
    """Callable shape of ``run_command``, injectable for deterministic tests."""

    def __call__(
        self, argv: Sequence[str], *, cwd: Path, timeout_seconds: float
    ) -> CommandOutcome: ...


def run_command(argv: Sequence[str], *, cwd: Path, timeout_seconds: float) -> CommandOutcome:
    """Run ``argv`` as a subprocess argument array and report its outcome.

    Args:
        argv: Full command and arguments; never a shell string.
        cwd: Working directory for the subprocess.
        timeout_seconds: Maximum wall-clock time to wait before the
            subprocess is killed and treated as unavailable.

    Returns:
        A ``CommandOutcome`` describing what happened. Never raises for a
        missing executable or a timeout; both become sanitized outcomes.
    """
    start = time.monotonic()
    try:
        completed = subprocess.run(
            list(argv),
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return CommandOutcome(None, timed_out=True, duration_seconds=time.monotonic() - start)
    except OSError:
        return CommandOutcome(None, timed_out=False, duration_seconds=time.monotonic() - start)
    return CommandOutcome(
        completed.returncode, timed_out=False, duration_seconds=time.monotonic() - start
    )
