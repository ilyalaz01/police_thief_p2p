"""Worked-vector regression for the local proposed final consensus scope."""

from __future__ import annotations

import hashlib
import json

from police_thief_lab.interop.artifacts import consensus_sha256, final_consensus_scope
from tests.support.project_paths import PROJECT_ROOT

ROOT = PROJECT_ROOT
VECTOR_PATH = ROOT / "interop/fixtures/final_consensus_scope_worked_vector.json"
IMPLEMENTED_SCOPE = "reference_symmetric_outcome_without_tie"
UNDEFINED_SCOPE = "reference_symmetric_rows_as_supplied_no_implicit_tie"


def test_final_consensus_scope_worked_vector_exact_bytes_and_hash() -> None:
    vector = json.loads(VECTOR_PATH.read_text(encoding="utf-8"))
    inputs = vector["input"]
    scope = final_consensus_scope(
        inputs["game_id"], inputs["aggregate"], inputs["sub_games"]
    )
    assert vector["scope_identifier"] == IMPLEMENTED_SCOPE
    assert scope == vector["expected_consensus_object"]
    preimage = json.dumps(scope, sort_keys=True, ensure_ascii=False).encode("utf-8")
    assert preimage.hex() == vector["expected_preimage_utf8_hex"]
    assert hashlib.sha256(preimage).hexdigest() == vector["expected_sha256"]
    assert consensus_sha256(scope) == vector["expected_sha256"]
    assert not set(vector["excluded_probe_fields"]) & set(scope["sub_games"][0])


def test_active_profile_and_runbook_use_only_implemented_scope_identifier() -> None:
    profile = json.loads(
        (ROOT / "interop/fixtures/phase4a5_reference_profile.json").read_text(encoding="utf-8")
    )
    runbook = (ROOT / "docs/REAL_TEAM_WARMUP_RUNBOOK.md").read_text(encoding="utf-8")
    assert profile["consensus_scope"] == IMPLEMENTED_SCOPE
    assert IMPLEMENTED_SCOPE in runbook
    assert UNDEFINED_SCOPE not in runbook
