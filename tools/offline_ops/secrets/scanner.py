"""Fail-closed filesystem walk for the scan-secrets command.

Traversal and matching use only ``pathlib``; pruned directories are never
descended into. Findings never carry matched text, only a sanitized
category and the file's path relative to the scan root.
"""

from __future__ import annotations

import dataclasses
import fnmatch
from collections.abc import Iterator
from pathlib import Path

from tools.offline_ops.secrets.patterns import (
    ARTIFACT_NAME_PREFIXES,
    CACHE_AND_TEMP_NAME_PATTERNS,
    NONCE_EXEMPT_TOP_LEVEL_DIR,
    NONCE_KEY_PATTERN,
    SKIP_DIRECTORY_NAMES,
    TUNNEL_CONFIG_NAME_PATTERNS,
    credential_patterns,
)

_MAX_SCANNED_FILE_BYTES = 5_000_000


@dataclasses.dataclass(frozen=True)
class SecretFinding:
    """One sanitized fail-closed finding. Never carries matched text."""

    relative_path: str
    category: str


def scan_path(
    root: Path, *, exclude_relative_dirs: frozenset[str] = frozenset()
) -> list[SecretFinding]:
    """Walk ``root`` and return every fail-closed finding, sanitized.

    Args:
        root: Directory to scan. Pruned directories (see
            ``SKIP_DIRECTORY_NAMES``) are never descended into.
        exclude_relative_dirs: Additional POSIX-style paths, relative to
            ``root``, to prune. Callers use this for directories that are
            known-safe by construction (e.g. this tool's own test fixtures
            for the scanner itself), never for arbitrary user exclusions.

    Returns:
        Findings sorted by relative path, then category.

    Raises:
        FileNotFoundError: If ``root`` does not exist.
    """
    if not root.exists():
        raise FileNotFoundError(root)

    findings = [
        finding
        for entry in _iter_files(root, exclude_relative_dirs)
        for finding in _scan_entry(root, entry)
    ]
    return sorted(findings, key=lambda finding: (finding.relative_path, finding.category))


def _iter_files(root: Path, exclude_relative_dirs: frozenset[str]) -> Iterator[Path]:
    stack = [root]
    while stack:
        current = stack.pop()
        for child in current.iterdir():
            if child.is_dir():
                relative = child.relative_to(root).as_posix()
                if child.name in SKIP_DIRECTORY_NAMES or relative in exclude_relative_dirs:
                    continue
                stack.append(child)
            else:
                yield child


def _scan_entry(root: Path, entry: Path) -> list[SecretFinding]:
    relative = str(entry.relative_to(root))

    if entry.is_symlink():
        return [SecretFinding(relative, "symlink")]
    if _escapes_root(root, entry):
        return [SecretFinding(relative, "path_traversal")]
    if _matches_any(entry.name, CACHE_AND_TEMP_NAME_PATTERNS):
        return [SecretFinding(relative, "cache_or_temp_file")]
    if _matches_any(entry.name, TUNNEL_CONFIG_NAME_PATTERNS):
        return [SecretFinding(relative, "tunnel_configuration")]
    return _scan_content(root, entry, relative)


def _escapes_root(root: Path, entry: Path) -> bool:
    try:
        entry.resolve().relative_to(root.resolve())
    except ValueError:
        return True
    return False


def _matches_any(name: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(name, pattern) for pattern in patterns)


def _scan_content(root: Path, entry: Path, relative: str) -> list[SecretFinding]:
    if entry.stat().st_size > _MAX_SCANNED_FILE_BYTES:
        return []
    try:
        text = entry.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    findings = [
        SecretFinding(relative, category)
        for category, pattern in credential_patterns().items()
        if pattern.search(text)
    ]
    if _is_non_artifact_nonce(entry, relative, text):
        findings.append(SecretFinding(relative, "non_artifact_nonce"))
    return findings


def _is_non_artifact_nonce(entry: Path, relative: str, text: str) -> bool:
    if entry.suffix != ".json" or not NONCE_KEY_PATTERN.search(text):
        return False
    if entry.name.startswith(ARTIFACT_NAME_PREFIXES):
        return False
    top_level = Path(relative).parts[0]
    return top_level != NONCE_EXEMPT_TOP_LEVEL_DIR
