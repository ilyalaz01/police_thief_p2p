"""Contract for role-specific README overlays and offline assembly guidance."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
POLICY_PATH = ROOT / "data/submission/role_content_policy.v1.json"
RUNBOOK_PATH = ROOT / "docs/ROLE_REPOSITORY_ASSEMBLY_RUNBOOK.md"
ROLE_READMES = {
    "police": ROOT / "submission/templates/police/README.md",
    "thief": ROOT / "submission/templates/thief/README.md",
}
ROLE_FACTS = {
    "police": ("ScentTacticalPolice", "FROZEN_ACCEPTED"),
    "thief": ("RandomLegalThief", "CURRENT_DEFAULT_NOT_NEW_CHAMPION"),
}


def load_policy() -> dict[str, object]:
    """Load the accepted candidate role-content policy."""
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def read_role(role: str) -> str:
    """Read one future root README overlay."""
    return ROLE_READMES[role].read_text(encoding="utf-8")


def test_role_templates_identify_only_the_observed_runtime_policy() -> None:
    for role, (runtime_policy, policy_status) in ROLE_FACTS.items():
        document = read_role(role)
        assert document.startswith(f"# Police-Thief P2P — {role.title()}\n")
        assert f"Runtime role: `{role}`" in document
        assert f"Runtime policy: `{runtime_policy}`" in document
        assert f"Policy status: `{policy_status}`" in document


def test_both_templates_cover_rules_49_and_50_without_fake_cross_links() -> None:
    for document in map(read_role, ROLE_READMES):
        assert "Rule 49" in document
        assert "Rule 50" in document
        assert "PENDING_HUMAN_APPROVAL" in document
        assert "placeholder is not a valid cross-link" in document
        for required in (
            "docs/PRD.md",
            "docs/PLAN.md",
            "docs/TODO.md",
            "config/",
        ):
            assert required in document


def test_templates_offer_only_safe_offline_commands() -> None:
    required_commands = (
        "uv sync",
        "peer_cli --help",
        "tests/system/test_phase4a_process.py",
        "tools.offline_ops.cli quality-gate",
        "viewer_cli live",
        "viewer_cli replay",
    )
    forbidden_operations = ("--public", "--real-team", "cloudflared", "gmail")
    for document in map(read_role, ROLE_READMES):
        for command in required_commands:
            assert command in document
        lowered = document.lower()
        assert all(operation not in lowered for operation in forbidden_operations)
        assert "not authorization" in lowered


def test_policy_points_to_the_exact_overlay_paths() -> None:
    roles = load_policy()["roles"]
    for role, path in ROLE_READMES.items():
        expected = path.relative_to(ROOT).as_posix()
        assert roles[role]["readme_overlay"] == expected


def test_assembly_runbook_preserves_history_and_human_gates() -> None:
    runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
    ordered_steps = (
        "Freeze the accepted shared commit",
        "Generate and review explicit manifests",
        "Produce offline candidate snapshots",
        "Create history-preserving role branches",
        "Apply the role README overlays",
        "Restore the pinned conformance submodule",
        "Run independent role gates",
        "Stop for exact-content and URL approval",
    )
    positions = [runbook.index(step) for step in ordered_steps]
    assert positions == sorted(positions)
    for fact in (
        "source_commit",
        "PENDING_HUMAN_APPROVAL",
        "v1.0-submission",
        "preserve contributor authorship",
        "tests/offline_ops/",
        "external/copthief-league-protocol",
    ):
        assert fact in runbook
    assert "No command in this runbook authorizes" in runbook
