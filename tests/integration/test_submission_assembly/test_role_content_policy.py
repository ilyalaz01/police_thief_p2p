"""Contract for the safe shared content of both future role repositories."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
POLICY_PATH = ROOT / "data/submission/role_content_policy.v1.json"
DOC_PATH = ROOT / "docs/ROLE_REPOSITORY_CONTENT_POLICY.md"
FORBIDDEN_PREFIXES = (
    ".agents/",
    ".codex/",
    "external/",
    "reports/",
    "sources/",
    "temp/",
    "tmp/",
)


def git(*args: str) -> str:
    """Run a read-only Git query against this checkout."""
    return subprocess.run(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", "-C", str(ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout


def policy() -> dict[str, object]:
    """Load the machine-readable candidate content policy."""
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def tracked_regular_files() -> set[str]:
    """Return tracked non-gitlink paths from the real index."""
    entries = git("ls-files", "--stage").splitlines()
    return {
        entry.split("\t", 1)[1]
        for entry in entries
        if entry.startswith(("100644 ", "100755 "))
    }


def resolved_files(data: dict[str, object]) -> set[str]:
    """Resolve the policy over tracked regular files without copying bytes."""
    content = data["shared_content"]
    tracked = tracked_regular_files()
    selected = set(content["include_exact"])
    selected.update(
        path
        for path in tracked
        if any(path.startswith(prefix) for prefix in content["include_prefixes"])
    )
    return {
        path
        for path in selected
        if path not in content["exclude_exact"]
        and not any(path.startswith(prefix) for prefix in content["exclude_prefixes"])
    }


def test_policy_is_pending_and_role_truth_is_observed() -> None:
    data = policy()
    roles = data["roles"]
    assert data["schema"] == "role_repository_content_policy_v1"
    assert data["status"] == "LOCAL_CANDIDATE_PENDING_EXPORT_TOOL_INTEGRATION"
    assert roles["police"]["runtime_policy"] == "ScentTacticalPolice"
    assert roles["police"]["policy_status"] == "FROZEN_ACCEPTED"
    assert roles["thief"]["runtime_policy"] == "RandomLegalThief"
    assert roles["thief"]["policy_status"] == "CURRENT_DEFAULT_NOT_NEW_CHAMPION"
    assert {role["counterpart_repository_url"] for role in roles.values()} == {
        "PENDING_HUMAN_APPROVAL"
    }


def test_candidate_satisfies_rule_50_and_preserves_evidence() -> None:
    selected = resolved_files(policy())
    required = {"README.md", "docs/PRD.md", "docs/PLAN.md", "docs/TODO.md"}
    assert required <= selected
    assert any(path.startswith("config/") for path in selected)
    for prefix in ("src/", "tests/", "tools/", "docs/images/", "results/research/"):
        assert any(path.startswith(prefix) for path in selected), prefix


def test_candidate_excludes_private_gitlink_and_synthetic_secret_fixtures() -> None:
    data = policy()
    selected = resolved_files(data)
    tracked = tracked_regular_files()
    assert selected <= tracked
    assert ".gitmodules" not in selected
    assert not any(path.startswith(FORBIDDEN_PREFIXES) for path in selected)
    assert not any(path.startswith("tests/offline_ops/") for path in selected)
    assert data["external_submodule"]["state"] == "REPROVISION_AFTER_EXPORT"


def test_cutoff_and_runtime_defaults_are_inspectable() -> None:
    data = policy()
    subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={ROOT.as_posix()}",
            "-C",
            str(ROOT),
            "merge-base",
            "--is-ancestor",
            data["evidence_cutoff"],
            "HEAD",
        ],
        check=True,
    )
    runtime = (ROOT / "src/police_thief_lab/interop/runtime.py").read_text(encoding="utf-8")
    assert "ScentTacticalPolice(seed) if role is Role.POLICE else RandomLegalThief(seed)" in runtime


def test_final_operations_remain_blocked_and_documented() -> None:
    data = policy()
    assert data["authorizations"] == {
        "create_final_repositories": False,
        "publish_exports": False,
        "create_submission_tags": False,
        "contact_opponents": False,
        "start_gmail": False,
        "start_gameplay": False,
    }
    document = DOC_PATH.read_text(encoding="utf-8")
    for fact in ("Rule 49", "Rule 50", "tests/offline_ops", "PENDING_HUMAN_APPROVAL"):
        assert fact in document
