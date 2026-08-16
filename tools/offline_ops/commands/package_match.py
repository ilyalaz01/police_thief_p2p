"""``package-match`` command.

Validate-then-atomically-package behavior for a match artifact directory
lands in RE-001 Phase 3.
"""

from __future__ import annotations

from pathlib import Path

from tools.offline_ops.commands._unimplemented import unimplemented_report
from tools.offline_ops.models import GateReport


def run(path: Path, output: Path) -> GateReport:
    """Return the not-yet-implemented report for ``package-match``.

    Args:
        path: Match artifact directory requested by the operator. Accepted
            now to keep the CLI contract stable; used starting in
            RE-001 Phase 3.
        output: Destination package directory requested by the operator.
            Accepted now to keep the CLI contract stable; used starting in
            RE-001 Phase 3.
    """
    del path, output
    return unimplemented_report("package-match", "RE-001 Phase 3")
