"""Contract for history-preserving Police and Thief repository candidates."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.support.role_manual import assert_complete_role_manual
from tools.submission_assembly.policy import build_export_manifest, role_overlay
from tools.submission_assembly.repository import verify_role_repository
from tools.submission_assembly.repository_cli import main as repository_cli
from tools.submission_export.git_ops import get_head_commit, get_tracked_info

POLICY = Path("data/submission/role_content_policy.v1.json")


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def _candidate(source: Path, destination: Path, role: str) -> tuple[Path, str]:
    source_commit = get_head_commit(source)
    subprocess.run(
        ["git", "clone", "--shared", "--no-checkout", str(source), str(destination)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    _git(destination, "switch", "-c", f"synthetic-{role}", source_commit)
    manifest = build_export_manifest(source / POLICY, role, source)
    regular, _gitlinks = get_tracked_info(destination)
    retained = set(manifest["include"]) | {".gitmodules"}
    removed = sorted(regular - retained)
    assert removed
    _git(destination, "rm", "--", *removed)
    overlay = source / role_overlay(source / POLICY, role)
    shutil.copyfile(overlay, destination / "README.md")
    _git(destination, "add", "README.md")
    _git(
        destination,
        "-c",
        "user.name=Synthetic Role Test",
        "-c",
        "user.email=synthetic-role@example.invalid",
        "commit",
        "-m",
        f"test: assemble {role} candidate",
    )
    return destination, source_commit


@pytest.mark.parametrize("role", ["police", "thief"])
def test_history_preserving_role_candidate_passes_exact_gate(
    role: str, repo_root: Path, tmp_path: Path
) -> None:
    candidate, source_commit = _candidate(repo_root, tmp_path / role, role)
    report = verify_role_repository(
        repo_root,
        candidate,
        repo_root / POLICY,
        role,
        source_commit,
    )
    assert report["schema"] == "role_repository_gate_v1"
    assert report["role"] == role
    assert report["source_commit"] == source_commit
    assert report["history_preserved"] is True
    assert report["submodule_pin"] == "PASS"
    assert report["secret_scan"] == "PASS"
    assert report["counterpart_repository_url"] == "PENDING_HUMAN_APPROVAL"
    assert_complete_role_manual((candidate / "README.md").read_text(encoding="utf-8"), role)


def test_role_policy_excludes_shared_assembly_only_code(repo_root: Path) -> None:
    manifest = build_export_manifest(repo_root / POLICY, "police", repo_root)
    excluded = (
        "tests/offline_ops/",
        "tests/integration/test_submission_assembly/",
        "tools/submission_assembly/",
    )
    assert not [path for path in manifest["include"] if path.startswith(excluded)]


def test_role_gate_refuses_dirty_candidate(repo_root: Path, tmp_path: Path) -> None:
    candidate, source_commit = _candidate(repo_root, tmp_path / "dirty", "police")
    (candidate / "README.md").write_text("tampered after commit\n", encoding="utf-8")
    with pytest.raises(ValueError, match="clean"):
        verify_role_repository(
            repo_root,
            candidate,
            repo_root / POLICY,
            "police",
            source_commit,
        )


def test_role_gate_cli_emits_sanitized_json(
    repo_root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    candidate, source_commit = _candidate(repo_root, tmp_path / "cli", "police")
    assert (
        repository_cli(
            [
                "--role",
                "police",
                "--candidate",
                str(candidate),
                "--source-commit",
                source_commit,
                "--source-root",
                str(repo_root),
                "--policy",
                str(repo_root / POLICY),
            ]
        )
        == 0
    )
    report = json.loads(capsys.readouterr().out)
    assert report["schema"] == "role_repository_gate_v1"
    assert report["external_operations_authorized"] is False
