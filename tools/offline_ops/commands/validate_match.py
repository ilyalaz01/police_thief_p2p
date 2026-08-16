"""``validate-match`` command.

Schema 1.1 four-artifact directory validation through the existing MIT
checker lands in RE-001 Phase 3.
"""

from __future__ import annotations

from pathlib import Path

from tools.offline_ops.commands._unimplemented import unimplemented_report
from tools.offline_ops.models import GateReport


def run(path: Path) -> GateReport:
    """Return the not-yet-implemented report for ``validate-match``.

    Args:
        path: Match artifact directory requested by the operator. Accepted
            now to keep the CLI contract stable; used starting in
            RE-001 Phase 3.
    """
    del path
    return unimplemented_report("validate-match", "RE-001 Phase 3")
