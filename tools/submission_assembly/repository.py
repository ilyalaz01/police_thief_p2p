"""Read-only gate for one history-preserving role repository candidate."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from tools.offline_ops.secrets.scanner import scan_path
from tools.submission_assembly.git_state import require_clean_worktree
from tools.submission_assembly.policy import build_export_manifest, role_overlay
from tools.submission_export.git_ops import get_head_commit, get_tracked_info

_GITMODULES = ".gitmodules"
_SUBMODULE = "external/copthief-league-protocol"


def verify_role_repository(
    source_root: Path,
    candidate_root: Path,
    policy_path: Path,
    role: str,
    source_commit: str,
) -> dict[str, object]:
    """Verify exact bytes, ancestry, submodule pin, hard stops, and privacy."""
    require_clean_worktree(source_root)
    require_clean_worktree(candidate_root)
    manifest = build_export_manifest(policy_path, role, source_root)
    if manifest["source_commit"] != source_commit:
        raise ValueError("source commit does not match the reviewed export manifest")
    _require_ancestor(candidate_root, source_commit)
    regular, gitlinks = get_tracked_info(candidate_root)
    expected_regular = set(manifest["include"]) | {_GITMODULES}
    if regular != expected_regular:
        raise ValueError("candidate regular-file set differs from the reviewed manifest")
    if gitlinks != frozenset({_SUBMODULE}):
        raise ValueError("candidate conformance submodule path is missing or unexpected")
    _require_bytes(source_root, candidate_root, policy_path, role, manifest)
    source_pin = _gitlink_oid(source_root)
    if _gitlink_oid(candidate_root) != source_pin:
        raise ValueError("candidate conformance submodule pin differs from source")
    if _tag_exists(candidate_root, "v1.0-submission"):
        raise ValueError("final submission tag exists before exact-content approval")
    findings = scan_path(candidate_root)
    if findings:
        categories = sorted({finding.category for finding in findings})
        raise ValueError(f"candidate secret scan failed by category: {categories!r}")
    files, aggregate = _tracked_hashes(candidate_root, expected_regular, source_pin)
    return {
        "schema": "role_repository_gate_v1",
        "role": role,
        "source_commit": source_commit,
        "candidate_commit": get_head_commit(candidate_root),
        "regular_file_count": len(files),
        "candidate_aggregate_hash": aggregate,
        "history_preserved": True,
        "submodule_pin": "PASS",
        "secret_scan": "PASS",
        "final_submission_tag": "ABSENT",
        "counterpart_repository_url": manifest["counterpart_repository_url"],
        "external_operations_authorized": False,
    }


def _require_bytes(
    source: Path,
    candidate: Path,
    policy_path: Path,
    role: str,
    manifest: dict[str, object],
) -> None:
    """Require selected source bytes except for the exact role README overlay."""
    overlay = source / role_overlay(policy_path, role)
    for relative in manifest["include"]:
        expected = overlay if relative == "README.md" else source / relative
        if expected.read_bytes() != (candidate / relative).read_bytes():
            raise ValueError(f"candidate byte mismatch: {relative!r}")
    if (source / _GITMODULES).read_bytes() != (candidate / _GITMODULES).read_bytes():
        raise ValueError("candidate .gitmodules bytes differ from source")


def _require_ancestor(candidate: Path, source_commit: str) -> None:
    """Require the accepted source commit to remain in candidate history."""
    result = _git(candidate, "merge-base", "--is-ancestor", source_commit, "HEAD", check=False)
    if result.returncode != 0:
        raise ValueError("candidate does not preserve accepted source history")


def _gitlink_oid(root: Path) -> str:
    """Return the exact tracked conformance gitlink object ID."""
    output = _git(root, "ls-files", "--stage", "--", _SUBMODULE).stdout.strip()
    fields = output.split()
    if len(fields) < 2 or fields[0] != "160000":
        raise ValueError("conformance path is not one pinned Git gitlink")
    return fields[1]


def _tag_exists(root: Path, tag: str) -> bool:
    """Return whether an exact local tag ref already exists."""
    result = _git(root, "show-ref", "--verify", "--quiet", f"refs/tags/{tag}", check=False)
    return result.returncode == 0


def _tracked_hashes(
    root: Path, regular: set[str], gitlink_oid: str
) -> tuple[list[dict[str, str]], str]:
    """Hash exact tracked regular bytes plus the pinned gitlink identity."""
    files = [
        {"path": path, "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}
        for path in sorted(regular)
    ]
    preimage = "".join(f"{item['path']}:{item['sha256']}\n" for item in files)
    preimage += f"{_SUBMODULE}:gitlink:{gitlink_oid}\n"
    return files, hashlib.sha256(preimage.encode()).hexdigest()


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run one local read-only Git query with safe-directory framing."""
    return subprocess.run(
        ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root), *args],
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
