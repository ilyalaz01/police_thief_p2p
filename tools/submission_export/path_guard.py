"""Fail-closed path security validation for the submission exporter.

Every check raises :class:`PathViolationError` with a category and a safe
truncated path only — never the full system path, username, or file body.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

_FORBIDDEN_PREFIXES: tuple[str, ...] = (
    ".git/",
    ".agents/",
    ".codex/",
    "sources/",
    "reports/",
    "tmp/",
    "temp/",
    "artifacts/",
    "logs/",
    "run-output/",
    "public-run/",
    "interop/logs/",
    ".venv/",
)

_CREDENTIAL_NAME_PATTERNS: tuple[str, ...] = (
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*.secret",
    "id_rsa*",
    "id_ed25519*",
    ".netrc",
    ".env",
    "*tunnel*.yml",
    "*tunnel*.yaml",
    "*tunnel*.json",
)


class PathViolationError(ValueError):
    """A path failed one of the exporter's fail-closed security checks."""

    def __init__(self, category: str, safe_path: str) -> None:
        self.category = category
        self.safe_path = safe_path
        super().__init__(f"{category}: {safe_path!r}")


def validate_path_string(s: str) -> None:
    """Raise :class:`PathViolationError` on any malformed path string.

    Checks: empty, absolute, drive-qualified, backslash, or ``..`` component.
    """
    if not s:
        raise PathViolationError("empty_path", "<empty>")
    if s.startswith("/") or s.startswith("\\"):
        raise PathViolationError("absolute_path", s[:60])
    if len(s) >= 2 and s[1] == ":":
        raise PathViolationError("drive_qualified_path", s[:60])
    if "\\" in s:
        raise PathViolationError("backslash_path", s[:60])
    if ".." in s.split("/"):
        raise PathViolationError("dotdot_component", s[:60])


def validate_include_set(
    paths: tuple[str, ...],
    repo_root: Path,
    regular_tracked: frozenset[str],
    gitlink_paths: frozenset[str],
) -> None:
    """Validate the full include set against all fail-closed rules.

    Args:
        paths: Sorted include paths from the manifest.
        repo_root: Absolute repository root used to check symlinks.
        regular_tracked: POSIX paths of regular tracked files from git index.
        gitlink_paths: POSIX paths of gitlink entries from git index.

    Raises:
        PathViolationError: On the first violation found.
    """
    seen: set[str] = set()
    seen_lower: dict[str, str] = {}
    for p in paths:
        validate_path_string(p)
        if p in seen:
            raise PathViolationError("duplicate_path", p[:60])
        lower = p.lower()
        if lower in seen_lower and seen_lower[lower] != p:
            raise PathViolationError("case_insensitive_collision", p[:60])
        seen.add(p)
        seen_lower[lower] = p
        _check_forbidden(p)
        if p in gitlink_paths:
            raise PathViolationError("gitlink_entry", p[:60])
        if p not in regular_tracked:
            raise PathViolationError("missing_or_untracked", p[:60])
        if (repo_root / p).is_symlink():
            raise PathViolationError("symlink", p[:60])


def _check_forbidden(path: str) -> None:
    """Raise PathViolationError if path matches a forbidden prefix or credential name."""
    for prefix in _FORBIDDEN_PREFIXES:
        if path.startswith(prefix) or path == prefix.rstrip("/"):
            raise PathViolationError("forbidden_prefix", path[:60])
    name = path.split("/")[-1]
    for pattern in _CREDENTIAL_NAME_PATTERNS:
        if fnmatch.fnmatch(name, pattern):
            raise PathViolationError("credential_or_secret", path[:60])
