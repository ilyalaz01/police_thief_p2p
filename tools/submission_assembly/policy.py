"""Resolve the reviewed role-content policy into explicit exporter inputs."""

from __future__ import annotations

import json
from pathlib import Path

from tools.submission_export.git_ops import get_head_commit, get_tracked_info

_POLICY_SCHEMA = "role_repository_content_policy_v1"
_POLICY_STATUS = "EXACT_ROLE_URLS_APPROVED_FOR_PUBLICATION"
_ROLES = frozenset({"police", "thief"})
_REQUIRED = ["README.md", "docs/PRD.md", "docs/PLAN.md", "docs/TODO.md"]
_COUNTERPART_URLS = {
    "police": "https://github.com/ilyalaz01/police_thief_p2p-thief",
    "thief": "https://github.com/ilyalaz01/police_thief_p2p-police",
}
_AUTHORIZATIONS = {
    "create_final_repositories": True,
    "publish_exports": True,
    "create_submission_tags": False,
    "contact_opponents": False,
    "start_gmail": False,
    "start_gameplay": False,
}


def load_policy(path: Path) -> dict[str, object]:
    """Load and fail closed on an unapproved or externally authorized policy."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != _POLICY_SCHEMA or data.get("status") != _POLICY_STATUS:
        raise ValueError("role-content policy schema or integration status is not accepted")
    authorizations = data.get("authorizations")
    if authorizations != _AUTHORIZATIONS:
        raise ValueError("role-content policy authorization boundary is not accepted")
    return data


def build_export_manifest(path: Path, role: str, repo_root: Path) -> dict[str, object]:
    """Build one explicit, sorted manifest from the reviewed tracked-file policy."""
    if role not in _ROLES:
        raise ValueError(f"unsupported candidate role: {role!r}")
    policy = load_policy(path)
    regular, _gitlinks = get_tracked_info(repo_root)
    content = _mapping(policy, "shared_content")
    selected = _resolve_selected(content, regular)
    role_policy = _mapping(_mapping(policy, "roles"), role)
    overlay = _string(role_policy, "readme_overlay")
    if overlay not in selected:
        raise ValueError("reviewed role README overlay is outside the selected file set")
    counterpart = _string(role_policy, "counterpart_repository_url")
    if counterpart != _COUNTERPART_URLS[role]:
        raise ValueError("candidate counterpart repository URL is not approved")
    return {
        "schema": "submission_export_v1",
        "role": role,
        "source_commit": get_head_commit(repo_root),
        "include": sorted(selected),
        "required_paths": list(_REQUIRED),
        "counterpart_repository_url": counterpart,
    }


def role_overlay(path: Path, role: str) -> str:
    """Return the validated POSIX path of one role's exact README overlay."""
    policy = load_policy(path)
    return _string(_mapping(_mapping(policy, "roles"), role), "readme_overlay")


def _resolve_selected(content: dict[str, object], regular: frozenset[str]) -> set[str]:
    """Resolve exact/prefix policy rules over tracked regular files."""
    exact = _strings(content, "include_exact")
    prefixes = _strings(content, "include_prefixes")
    excluded = set(_strings(content, "exclude_exact"))
    excluded_prefixes = _strings(content, "exclude_prefixes")
    missing = sorted(set(exact) - regular)
    if missing:
        raise ValueError(f"reviewed exact include is not a tracked regular file: {missing[0]!r}")
    selected = set(exact)
    selected.update(path for path in regular if any(path.startswith(p) for p in prefixes))
    return {
        path
        for path in selected
        if path not in excluded and not any(path.startswith(p) for p in excluded_prefixes)
    }


def _mapping(data: dict[str, object], key: str) -> dict[str, object]:
    """Return one required object field or fail with a safe category."""
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"policy field must be an object: {key!r}")
    return value


def _strings(data: dict[str, object], key: str) -> tuple[str, ...]:
    """Return one required string-list field as an immutable tuple."""
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"policy field must be a string list: {key!r}")
    return tuple(value)


def _string(data: dict[str, object], key: str) -> str:
    """Return one required string field or fail closed."""
    value = data.get(key)
    if not isinstance(value, str):
        raise ValueError(f"policy field must be a string: {key!r}")
    return value
