"""Atomic two-role candidate assembly with deterministic root evidence."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from tools.submission_assembly.git_state import require_clean_worktree
from tools.submission_assembly.role import prepare_role

_ROLES = ("police", "thief")


def prepare_candidates(policy_path: Path, output: Path, repo_root: Path) -> dict[str, object]:
    """Atomically prepare both offline candidates from one exact clean commit."""
    if output.exists():
        raise ValueError("candidate output path must not already exist")
    require_clean_worktree(repo_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output.name}-", dir=output.parent))
    try:
        candidates = {
            role: prepare_role(policy_path, role, stage / role, repo_root) for role in _ROLES
        }
        source_commits = {str(item["source_commit"]) for item in candidates.values()}
        if len(source_commits) != 1:
            raise ValueError("role candidates were not assembled from one source commit")
        root_manifest = {
            "schema": "role_candidate_assembly_v1",
            "source_commit": source_commits.pop(),
            "roles": {
                role: {
                    "candidate_aggregate_hash": item["candidate_aggregate_hash"],
                    "file_count": item["file_count"],
                    "counterpart_repository_url": item["counterpart_repository_url"],
                }
                for role, item in candidates.items()
            },
            "external_operations_authorized": False,
        }
        (stage / "assembly_manifest.json").write_text(
            json.dumps(root_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        stage.replace(output)
        return root_manifest
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
