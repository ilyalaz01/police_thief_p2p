"""Official artifact filename grammar (book App. F table 20).

Mirrors the naming shape used by the MIT checker's own ``NAME_RE`` in
``external/copthief-league-protocol/tools/check_artifacts.py``: a filename
constant, not a reimplementation of that checker's semantic validation.
"""

from __future__ import annotations

import re

ARTIFACT_NAME_RE = re.compile(
    r"^(declaration|config|log|result)_(?P<gid>.+?)(?:_g(?P<nn>\d+))?\.json$"
)
