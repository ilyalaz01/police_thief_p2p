"""Contract for deterministic offline Police and Thief candidate trees."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.offline_ops.secrets.scanner import scan_path
from tools.submission_assembly.assembly import prepare_candidates
from tools.submission_assembly.policy import build_export_manifest

POLICY = Path("data/submission/role_content_policy.v1.json")
ROLES = ("police", "thief")


@pytest.fixture(scope="module")
def candidates(repo_root: Path, tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build both candidates once from the exact clean test commit."""
    output = tmp_path_factory.mktemp("candidate-parent") / "candidates"
    prepare_candidates(repo_root / POLICY, output, repo_root)
    return output


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative_files(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def test_policy_builds_explicit_reviewable_manifests(repo_root: Path) -> None:
    for role in ROLES:
        manifest = build_export_manifest(repo_root / POLICY, role, repo_root)
        assert manifest["schema"] == "submission_export_v1"
        assert manifest["role"] == role
        assert manifest["include"] == sorted(manifest["include"])
        assert manifest["counterpart_repository_url"] == "PENDING_HUMAN_APPROVAL"
        assert manifest["required_paths"] == [
            "README.md",
            "docs/PRD.md",
            "docs/PLAN.md",
            "docs/TODO.md",
        ]
        assert not any(path.startswith("tests/offline_ops/") for path in manifest["include"])
        assert "submission/templates/police/README.md" in manifest["include"]
        assert "submission/templates/thief/README.md" in manifest["include"]


def test_candidates_match_manifests_and_exact_role_overlays(
    candidates: Path, repo_root: Path
) -> None:
    for role in ROLES:
        role_root = candidates / role
        tree = role_root / "tree"
        evidence = role_root / "evidence"
        explicit = _json(evidence / "export_input.json")
        final = _json(evidence / "candidate_manifest.json")
        assert _relative_files(tree) == set(explicit["include"])
        assert (tree / "README.md").read_bytes() == (
            repo_root / f"submission/templates/{role}/README.md"
        ).read_bytes()
        assert final["schema"] == "role_candidate_manifest_v1"
        assert final["role"] == role
        assert final["counterpart_repository_url"] == "PENDING_HUMAN_APPROVAL"
        assert final["secret_scan"] == "PASS"
        assert not (tree / "export_manifest.json").exists()
        assert scan_path(tree) == []


def test_two_reproductions_have_byte_identical_evidence(
    candidates: Path, repo_root: Path, tmp_path: Path
) -> None:
    reproduced = tmp_path / "reproduced"
    prepare_candidates(repo_root / POLICY, reproduced, repo_root)
    for relative in (
        "assembly_manifest.json",
        "police/evidence/export_input.json",
        "police/evidence/export_plan.json",
        "police/evidence/candidate_manifest.json",
        "thief/evidence/export_input.json",
        "thief/evidence/export_plan.json",
        "thief/evidence/candidate_manifest.json",
    ):
        assert (candidates / relative).read_bytes() == (reproduced / relative).read_bytes()


def test_prepare_refuses_existing_output(repo_root: Path, tmp_path: Path) -> None:
    output = tmp_path / "existing"
    output.mkdir()
    with pytest.raises(ValueError, match="output"):
        prepare_candidates(repo_root / POLICY, output, repo_root)
