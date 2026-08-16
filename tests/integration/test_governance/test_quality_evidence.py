"""Quality-evidence contracts required by the project guidelines."""

from __future__ import annotations

import json
from pathlib import Path

from tests.support.project_paths import PROJECT_ROOT

CRITICAL_CASES = {
    "RULES-46-47": (
        "tests/integration/test_interop/test_phase4a_runtime_rules.py",
        "test_rule46_and_rule47_terminal_are_processed_before_strategy",
    ),
    "OBSERVATION-ISOLATION": (
        "tests/unit/test_game/test_observation.py",
        "test_observation_schema_has_no_opponent_position",
    ),
    "PROFILE-MISMATCH": (
        "tests/integration/test_interop/test_phase4a_runtime_network.py",
        "test_real_negotiation_mismatch_is_rejected_before_play",
    ),
    "RETRY-DEADLINE": (
        "tests/integration/test_interop/test_phase4a_runtime_rules.py",
        "test_turn_timeout_path_uses_monotonic_deadline",
    ),
    "DUPLICATE-EQUIVOCATION": (
        "tests/integration/test_interop/test_phase4a_crypto_protocol.py",
        "test_delivery_duplicate_equivocation_buffer_stale_and_window",
    ),
    "AUDIT-REPLAY": (
        "tests/integration/test_artifacts/test_phase4a_boundary_audit_artifacts.py",
        "test_tampered_nonce_payload_and_replay_are_rejected",
    ),
    "ARTIFACT-HASH-DOMAINS": (
        "tests/integration/test_artifacts/test_profile_hash_domains.py",
        "test_three_hash_domains_have_exact_distinct_lengths_bytes_and_hashes",
    ),
    "BACKPRESSURE": (
        "tests/integration/test_configuration/test_gatekeeper.py",
        "test_inbound_peer_queues_apply_bounded_fifo_backpressure_without_dropping",
    ),
    "LOCAL-PROCESS": (
        "tests/system/test_phase4a_process.py",
        "test_two_real_independent_processes_complete_localhost_game",
    ),
}


def test_critical_path_map_links_to_live_test_cases() -> None:
    mapping = (PROJECT_ROOT / "docs/QUALITY_CRITICAL_PATHS.md").read_text(encoding="utf-8")
    for identifier, (relative, test_name) in CRITICAL_CASES.items():
        assert f"`{identifier}`" in mapping
        assert f"`{relative}::{test_name}`" in mapping
        source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert f"def {test_name}(" in source


def test_quality_plan_defines_sanitized_failure_retention() -> None:
    plan = (PROJECT_ROOT / "docs/QUALITY_PLAN.md").read_text(encoding="utf-8")
    for requirement in (
        "Sanitized report retention",
        "failed run remains retained",
        "linked successful rerun",
        "must not contain raw stdout or stderr",
        "JUnit XML",
    ):
        assert requirement in plan


def test_quality_audit_is_machine_readable_and_operation_safe() -> None:
    audit_path = PROJECT_ROOT / "docs/audits/phase4d3_test_quality.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["phase"] == "4D3"
    assert audit["status"] == "GREEN"
    assert audit["tests"]["passed"] >= 191
    assert audit["tests"]["failed"] == 0
    assert audit["coverage"]["branch_percent"] >= 85
    assert audit["ruff"]["errors"] == 0
    assert audit["frozen_manifest"] == "7/7"
    assert audit["hcommit"] == "5/5"
    assert audit["conformance"] == "125/125"
    assert all(not audit["operations"][key] for key in audit["operations"])
