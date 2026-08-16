"""``scan-secrets`` command.

The fail-closed credential/nonce/tunnel scanner lands in RE-001 Phase 2.
"""

from __future__ import annotations

from pathlib import Path

from tools.offline_ops.commands._unimplemented import unimplemented_report
from tools.offline_ops.models import GateReport


def run(path: Path) -> GateReport:
    """Return the not-yet-implemented report for ``scan-secrets``.

    Args:
        path: Target path requested by the operator. Accepted now to keep
            the CLI contract stable; used starting in RE-001 Phase 2.
    """
    del path
    return unimplemented_report("scan-secrets", "RE-001 Phase 2")
