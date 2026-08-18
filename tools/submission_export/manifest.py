"""Manifest loading and schema validation for submission_export_v1.

The manifest is the only authoritative input for the exporter; the tool
never infers or guesses role contents.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

_VALID_ROLES = frozenset({"police", "thief"})
_SCHEMA = "submission_export_v1"


class ManifestError(ValueError):
    """Manifest failed schema or semantic validation."""


@dataclasses.dataclass(frozen=True)
class ExportManifest:
    """Validated, immutable representation of one submission_export_v1 manifest."""

    role: str
    source_commit: str
    include: tuple[str, ...]
    required_paths: tuple[str, ...]
    counterpart_repository_url: str


def load_and_validate(source: Path | dict[str, object]) -> ExportManifest:
    """Load a manifest from a path or dict and validate all fields.

    Args:
        source: Path to a JSON manifest file or an already-parsed dict.

    Returns:
        A validated, immutable :class:`ExportManifest`.

    Raises:
        ManifestError: If any field is missing, wrong type, or violates schema.
        FileNotFoundError: If *source* is a Path that does not exist.
        json.JSONDecodeError: If *source* is a Path to invalid JSON.
    """
    if isinstance(source, Path):
        data: dict[str, object] = json.loads(source.read_text(encoding="utf-8"))
    else:
        data = dict(source)

    _require_str(data, "schema")
    if data["schema"] != _SCHEMA:
        raise ManifestError(f"unsupported schema: {data['schema']!r}")

    _require_str(data, "role")
    if data["role"] not in _VALID_ROLES:
        raise ManifestError(f"unsupported role: {data['role']!r}")

    _require_str(data, "source_commit")
    commit = str(data["source_commit"])
    _hex_chars = frozenset("0123456789abcdefABCDEF")
    if len(commit) != 40 or not all(c in _hex_chars for c in commit):
        raise ManifestError("source_commit must be a 40-character hex SHA")

    _require_list_of_str(data, "include")
    _require_list_of_str(data, "required_paths")
    _require_str(data, "counterpart_repository_url")

    return ExportManifest(
        role=str(data["role"]),
        source_commit=str(data["source_commit"]),
        include=tuple(sorted(str(p) for p in data["include"])),  # type: ignore[arg-type]
        required_paths=tuple(str(p) for p in data["required_paths"]),  # type: ignore[arg-type]
        counterpart_repository_url=str(data["counterpart_repository_url"]),
    )


def _require_str(data: dict[str, object], key: str) -> None:
    """Raise ManifestError if *key* is absent or not a str."""
    if key not in data or not isinstance(data[key], str):
        raise ManifestError(f"missing or non-string field: {key!r}")


def _require_list_of_str(data: dict[str, object], key: str) -> None:
    """Raise ManifestError if *key* is absent, not a list, or has non-str items."""
    if key not in data or not isinstance(data[key], list):
        raise ManifestError(f"missing or non-list field: {key!r}")
    if not all(isinstance(v, str) for v in data[key]):  # type: ignore[union-attr]
        raise ManifestError(f"field {key!r} must contain only strings")
