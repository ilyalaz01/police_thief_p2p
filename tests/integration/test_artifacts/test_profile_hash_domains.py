"""Regression evidence separating fixture, runtime-profile, and terms hash domains."""

from __future__ import annotations

import hashlib
import json

from police_thief_lab.interop.artifacts import build_config_artifact
from police_thief_lab.interop.crypto import canonical_json
from police_thief_lab.interop.profile import MatchProfile
from tests.support.project_paths import PROJECT_ROOT

ROOT = PROJECT_ROOT
PROFILE_PATH = ROOT / "interop/fixtures/phase4a5_reference_profile.json"
WORKSHEET_PATH = ROOT / "interop/templates/real_team_uncounted_compatibility_worksheet.json"

EXPECTED = {
    "fixture": (717, "d20b039b48da09cbff7aa540f34863a7466d71b2ca90557b5f4d4c9afb69bc71"),
    "runtime": (772, "0cf0f86401039d3f3044caf4b55b3c472640ea6ea81724a82e9195175a2cb96a"),
    "terms": (284, "b97de3f6bb3e3aaed0c3f2e6ab2eee05d65aa1e7853e009ef448c42058c340c0"),
}


def _domains() -> tuple[bytes, MatchProfile, bytes, bytes]:
    fixture_bytes = PROFILE_PATH.read_bytes()
    profile = MatchProfile(**json.loads(fixture_bytes))
    runtime_bytes = profile.bytes()
    terms_bytes = canonical_json(profile.reference_terms()).encode("utf-8")
    return fixture_bytes, profile, runtime_bytes, terms_bytes


def test_three_hash_domains_have_exact_distinct_lengths_bytes_and_hashes() -> None:
    fixture_bytes, _profile, runtime_bytes, terms_bytes = _domains()
    domains = {"fixture": fixture_bytes, "runtime": runtime_bytes, "terms": terms_bytes}
    for name, value in domains.items():
        assert len(value) == EXPECTED[name][0]
        assert hashlib.sha256(value).hexdigest() == EXPECTED[name][1]
    assert len(set(domains.values())) == 3
    assert len({hashlib.sha256(value).hexdigest() for value in domains.values()}) == 3


def test_fixture_and_runtime_bytes_parse_to_same_logical_profile() -> None:
    fixture_bytes, profile, runtime_bytes, _terms_bytes = _domains()
    assert fixture_bytes != runtime_bytes
    assert json.loads(fixture_bytes) == json.loads(runtime_bytes) == profile.object()


def test_agreement_advertises_exact_runtime_extended_lock() -> None:
    _fixture_bytes, profile, runtime_bytes, _terms_bytes = _domains()
    identity = profile.agreement("police")["identity"]
    assert identity["config_sha256"] == EXPECTED["runtime"][1] == profile.sha256
    assert identity["config_bytes_hex"] == runtime_bytes.hex()


def test_schema_1_1_config_builder_uses_canonical_reference_terms_hash() -> None:
    _fixture_bytes, profile, _runtime_bytes, terms_bytes = _domains()
    artifact = build_config_artifact(profile.reference_terms(), "game", "uid", 1)
    assert artifact["schema_version"] == "1.1"
    assert artifact["config_sha256"] == EXPECTED["terms"][1]
    assert artifact["config_sha256"] == hashlib.sha256(terms_bytes).hexdigest()


def test_worksheet_domains_approvals_and_active_instructions_are_unambiguous() -> None:
    fixture_bytes, profile, runtime_bytes, terms_bytes = _domains()
    worksheet = json.loads(WORKSHEET_PATH.read_text(encoding="utf-8"))
    fixture = worksheet["fixture_file_provenance"]
    runtime = worksheet["runtime_extended_profile_lock"]
    terms = worksheet["official_reference_terms_lock"]
    assert fixture["status"] == "LOCAL_ONLY_NOT_NEGOTIATED"
    assert fixture["bilateral_config_or_profile_hash"] is False
    assert (fixture["byte_length"], fixture["sha256"]) == EXPECTED["fixture"]
    assert (runtime["byte_length"], runtime["sha256"]) == EXPECTED["runtime"]
    assert runtime["config_bytes_hex"] == runtime_bytes.hex()
    assert runtime["professor_omission_is_implicit_approval"] is False
    assert (terms["byte_length"], terms["sha256"]) == EXPECTED["terms"]
    assert terms["terms_object"] == profile.reference_terms()
    assert hashlib.sha256(fixture_bytes).hexdigest() == fixture["sha256"]
    assert hashlib.sha256(terms_bytes).hexdigest() == terms["sha256"]
    for section in (runtime, terms):
        assert all(value is None for key, value in section.items() if "approves" in key)
    assert worksheet["approval_status"] == "PENDING_BILATERAL_APPROVAL"
    assert worksheet["readiness_result"] == "BLOCKED_PENDING_HUMAN_INPUT"
    active = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in (
            "docs/REAL_TEAM_COMPATIBILITY_WORKSHEET.md",
            "docs/REAL_TEAM_WARMUP_RUNBOOK.md",
        )
    )
    assert "pretty profile bytes and SHA-256" not in active
    assert "byte-identical profile" not in active
    assert "fixture_file_provenance" in active
    assert "runtime_extended_profile_lock" in active
    assert "official_reference_terms_lock" in active
