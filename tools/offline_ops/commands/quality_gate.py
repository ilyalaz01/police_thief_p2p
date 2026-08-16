"""``quality-gate`` command.

Composition of pytest, Ruff, Hcommit vectors, the frozen manifest, the
conformance kit, and the secret scan lands in RE-001 Phase 2.
"""

from __future__ import annotations

from tools.offline_ops.commands._unimplemented import unimplemented_report
from tools.offline_ops.models import GateReport


def run() -> GateReport:
    """Return the not-yet-implemented report for ``quality-gate``."""
    return unimplemented_report("quality-gate", "RE-001 Phase 2")
