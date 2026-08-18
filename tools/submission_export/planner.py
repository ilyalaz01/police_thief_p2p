"""Deterministic plan operation for the offline submission exporter.

The plan validates an explicit manifest and returns a deterministic,
sorted JSON-serialisable description of what would be exported, including
per-file SHA-256 hashes and an aggregate manifest hash.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from tools.submission_export.git_ops import get_head_commit, get_tracked_info
from tools.submission_export.manifest import ExportManifest, ManifestError, load_and_validate
from tools.submission_export.path_guard import validate_include_set

_RULE_50_REQUIRED: frozenset[str] = frozenset(
    {"README.md", "docs/PRD.md", "docs/PLAN.md", "docs/TODO.md"}
)


def plan(source: Path | dict[str, object], repo_root: Path) -> dict[str, object]:
    """Validate a manifest and return a deterministic export plan.

    The plan is JSON-serialisable, deterministically sorted, and contains
    a per-file SHA-256 hash plus an aggregate hash over all entries.
    The counterpart URL is preserved verbatim; a PENDING value is never
    treated as approval.

    Args:
        source: Manifest path or already-parsed dict.
        repo_root: Absolute path to the repository root.

    Returns:
        A deterministic JSON-serialisable plan dict.

    Raises:
        ManifestError: Manifest validation fails or a Rule 50 path is absent.
        PathViolationError: A path fails a fail-closed security check.
        ValueError: source_commit does not match current HEAD.
    """
    manifest = load_and_validate(source)
    _assert_head_matches(manifest, repo_root)
    regular_tracked, gitlinks = get_tracked_info(repo_root)
    validate_include_set(manifest.include, repo_root, regular_tracked, gitlinks)
    _check_rule50(manifest)
    files = _hash_files(manifest.include, repo_root)
    return {
        "schema": "submission_export_plan_v1",
        "role": manifest.role,
        "source_commit": manifest.source_commit,
        "counterpart_repository_url": manifest.counterpart_repository_url,
        "files": files,
        "aggregate_hash": _aggregate_hash(files),
    }


def _assert_head_matches(manifest: ExportManifest, repo_root: Path) -> None:
    """Raise ValueError if source_commit does not equal the current HEAD."""
    head = get_head_commit(repo_root)
    if head != manifest.source_commit:
        raise ValueError(
            f"source_commit mismatch: manifest has {manifest.source_commit!r} "
            f"but HEAD is {head!r}"
        )


def _check_rule50(manifest: ExportManifest) -> None:
    """Raise ManifestError if any Rule 50 required path is absent from include."""
    include_set = set(manifest.include)
    for req in sorted(_RULE_50_REQUIRED):
        if req not in include_set:
            raise ManifestError(f"required Rule 50 path missing from include: {req!r}")
    if not any(p.startswith("config/") for p in include_set):
        raise ManifestError("required Rule 50 path missing from include: 'config/'")
    for req in manifest.required_paths:
        if req not in include_set:
            raise ManifestError(f"declared required_path missing from include: {req!r}")


def _hash_files(include: tuple[str, ...], repo_root: Path) -> list[dict[str, str]]:
    """Return a sorted list of {path, sha256} dicts for every included file."""
    result = []
    for posix_path in sorted(include):
        raw = (repo_root / posix_path).read_bytes()
        result.append({"path": posix_path, "sha256": hashlib.sha256(raw).hexdigest()})
    return result


def _aggregate_hash(files: list[dict[str, str]]) -> str:
    """Return a deterministic SHA-256 over the sorted path:sha256 preimage."""
    h = hashlib.sha256()
    for entry in sorted(files, key=lambda e: e["path"]):
        h.update(f"{entry['path']}:{entry['sha256']}\n".encode())
    return h.hexdigest()
