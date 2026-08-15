"""Offline invariants for the uncounted real-team compatibility worksheet."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
TEMPLATE_PATH = ROOT / "interop/templates/real_team_uncounted_compatibility_worksheet.json"
PROFILE_PATH = ROOT / "interop/fixtures/phase4a5_reference_profile.json"
B0_PATH = ROOT / "interop/fixtures/final_consensus_scope_worked_vector.json"


def _worksheet() -> dict:
    return json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))


def test_worksheet_is_unsigned_unapproved_and_always_blocked() -> None:
    worksheet = _worksheet()
    assert worksheet["document_kind"] == "OFFLINE_OPERATOR_WORKSHEET"
    assert worksheet["session_type"] == "UNCOUNTED"
    assert worksheet["approval_status"] == "PENDING_BILATERAL_APPROVAL"
    assert worksheet["is_agreement"] is False
    assert worksheet["is_signed"] is False
    assert worksheet["wire_artifact"] is False
    assert worksheet["readiness_result"] == "BLOCKED_PENDING_HUMAN_INPUT"
    assert worksheet["readiness_policy"]["template_is_always_blocked"] is True
    assert worksheet["readiness_policy"]["automatic_resolution"] is False


def test_worksheet_fabricates_no_team_or_approval_data() -> None:
    worksheet = _worksheet()
    for team in worksheet["teams"].values():
        assert team["group_id"] == team["group_name"] == ""
        assert team["repository_urls"] == {"police": "", "thief": ""}
        assert team["exact_advertised_git_commit"] == ""
        assert team["role"] == team["stable_public_https_mcp_url"] == ""
        assert team["identity_evidence"] == ""
        assert team["operator_approval"] is None
    serialized = json.dumps(worksheet).lower()
    assert "https://" not in serialized
    assert "credential" not in serialized
    assert '"token"' not in serialized
    assert '"nonce"' not in serialized
    for section_name in ("runtime_extended_profile_lock", "official_reference_terms_lock"):
        for key, value in worksheet[section_name].items():
            if key.startswith("team_") and "approv" in key:
                assert value is None
    assert all(
        item["team_a_approval"] is None and item["team_b_approval"] is None
        for item in worksheet["referenced_interoperability_items"]
    )


def test_worksheet_transport_and_operator_data_are_outside_profile_locks() -> None:
    worksheet = _worksheet()
    profile = json.loads(PROFILE_PATH.read_bytes())
    assert "stable_public_https_mcp_url" not in json.dumps(profile)
    locks = {
        key: worksheet[key]
        for key in (
            "fixture_file_provenance",
            "runtime_extended_profile_lock",
            "official_reference_terms_lock",
        )
    }
    assert "stable_public_https_mcp_url" not in json.dumps(locks)
    assert "operator_metadata" not in json.dumps(locks)
    assert worksheet["scope_boundaries"]["match_profile_contains_transport_endpoints"] is False
    assert worksheet["scope_boundaries"]["match_profile_contains_operator_metadata"] is False


def test_rule47_and_consensus_disagreements_cannot_be_auto_resolved() -> None:
    worksheet = _worksheet()
    rule47 = worksheet["mandatory_rules"]["rule_47"]
    assert rule47["mandatory"] is True
    assert rule47["team_a_confirms"] is None and rule47["team_b_confirms"] is None
    assert "disable" not in json.dumps(rule47).lower()
    b0 = json.loads(B0_PATH.read_text(encoding="utf-8"))
    consensus = worksheet["artifact_and_consensus"]
    assert consensus["artifact_schema"] == "1.1"
    assert consensus["mutual_agreement_representation"] == "object"
    assert consensus["consensus_scope_identifier"] == b0["scope_identifier"]
    assert consensus["worked_vector_expected_sha256"] == b0["expected_sha256"]
    assert consensus["consensus_scope_status"] == (
        "LOCAL_PROPOSAL_PENDING_EXPLICIT_BILATERAL_AGREEMENT"
    )
    assert consensus["opponent_accepts_exact_scope_object"] is None
    assert consensus["opponent_accepts_exact_serialization"] is None
    assert consensus["opponent_accepts_exact_hash_vector"] is None
    assert consensus["opponent_tie_treatment"] == ""
    assert consensus["opponent_proposes_different_scope"] == ""
    assert consensus["different_or_missing_response_status"] == "BLOCKING"
    assert worksheet["readiness_policy"]["missing_response"] == "BLOCKING"
    assert worksheet["readiness_policy"]["different_scope_response"] == "BLOCKING"
