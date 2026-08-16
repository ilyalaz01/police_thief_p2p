"""Make the repository root importable so ``tools.offline_ops`` resolves.

The offline-ops CLI is intentionally outside the packaged
``police_thief_lab`` distribution (see the module boundary in
``docs/RELEASE_ENGINEERING_WORKSTREAM.md``), so pytest's own per-test
import-path insertion never reaches it. This conftest adds only the
repository root to ``sys.path``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
