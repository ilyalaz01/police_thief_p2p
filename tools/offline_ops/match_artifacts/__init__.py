"""Filesystem-hygiene and packaging support for match artifact commands.

Semantic/cross-artifact validation is never reimplemented here: it is
composed from the existing MIT-licensed
``external/copthief-league-protocol/tools/check_artifacts.py`` checker.
This package only adds the filesystem-safety layer that checker does not
claim to provide (symlinks, path escapes, unexpected files, size/count
caps), plus atomic packaging of an already-validated directory.
"""

from __future__ import annotations
