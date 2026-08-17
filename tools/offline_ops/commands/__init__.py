"""Per-subcommand implementations for the offline-ops CLI.

Each module exposes a ``run`` function returning a ``GateReport``. Phase 1
ships stub implementations that report ``CheckStatus.UNAVAILABLE``; later
phases replace the stub bodies without changing the ``run`` signature or
the CLI dispatch contract.
"""

from __future__ import annotations
