"""Fail-closed filesystem hygiene checks for a match artifact directory.

Covers exactly what the composed MIT checker does not claim to: unexpected
files, symlinks, path escapes, oversized files, and file-count/total-size
caps. Content and cross-artifact semantics remain that checker's job.

Only the top level of the directory is inspected, matching the checker's
own "one flat directory" design (its own archive-exclusion contract): a
nested directory here is itself an unexpected entry, not a place to
recurse into.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

from tools.offline_ops.fs_safety import escapes_root
from tools.offline_ops.match_artifacts.naming import ARTIFACT_NAME_RE

#: A single sub-game log can legitimately be large; this stays generous.
MAX_ARTIFACT_FILE_BYTES = 10_000_000
MAX_TOTAL_BYTES = 50_000_000
MAX_FILE_COUNT = 500


@dataclasses.dataclass(frozen=True)
class HygieneFinding:
    """One sanitized fail-closed hygiene finding."""

    relative_path: str
    category: str


def scan_artifact_directory(root: Path) -> list[HygieneFinding]:
    """Return every fail-closed hygiene finding for ``root``'s top level.

    Raises:
        FileNotFoundError: If ``root`` does not exist or is not a directory.
    """
    if not root.is_dir():
        raise FileNotFoundError(root)

    entries = sorted(root.iterdir())
    if len(entries) > MAX_FILE_COUNT:
        return [HygieneFinding(".", "too_many_files")]

    findings = [finding for entry in entries for finding in _scan_entry(root, entry)]

    total_bytes = sum(entry.stat().st_size for entry in entries if entry.is_file())
    if total_bytes > MAX_TOTAL_BYTES:
        findings.append(HygieneFinding(".", "oversized_total"))
    return findings


def _scan_entry(root: Path, entry: Path) -> list[HygieneFinding]:
    relative = entry.name

    # Escape is checked before a bare symlink check: for a top-level-only
    # scan, only a symlink can ever resolve outside root, so an escaping
    # symlink is classified by the more specific, more severe category
    # ("path_traversal"); a symlink that stays inside root is "symlink".
    if escapes_root(root, entry):
        return [HygieneFinding(relative, "path_traversal")]
    if entry.is_symlink():
        return [HygieneFinding(relative, "symlink")]
    if entry.is_dir():
        return [HygieneFinding(relative, "unexpected_file")]
    if not ARTIFACT_NAME_RE.match(entry.name):
        return [HygieneFinding(relative, "unexpected_file")]
    if entry.stat().st_size > MAX_ARTIFACT_FILE_BYTES:
        return [HygieneFinding(relative, "oversized_file")]
    return []
