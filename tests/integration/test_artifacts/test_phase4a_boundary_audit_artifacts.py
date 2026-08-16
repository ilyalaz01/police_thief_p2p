"""Phase 4A boundary, audit, replay, and artifact checks."""

import json
from dataclasses import fields
from pathlib import Path

from police_thief_lab import GameConfig, Observation, Role, Simulator
from police_thief_lab.interop.artifacts import (
    canonical_sha256,
    consensus_sha256,
    pretty_bytes,
    write_artifacts,
)
from police_thief_lab.interop.crypto import canonical_json, seal, verify_records
from police_thief_lab.interop.replay import replay_sequence, verify_audit
from police_thief_lab.policies.tactical import ScentTacticalPolice
from tests.support.interop_test_support import profile


def test_strategy_boundary_contains_only_legal_observation() -> None:
    simulator = Simulator(GameConfig())
    simulator.apply(simulator.observe(Role.THIEF).legal_actions[-1])
    observation = simulator.observe(Role.POLICE)
    names = {field.name for field in fields(Observation)}
    assert not {"world_state", "opponent_position", "audit", "remote_peer"} & names
    assert ScentTacticalPolice(1).choose_action(observation) in observation.legal_actions


def test_tampered_nonce_payload_and_replay_are_rejected() -> None:
    record = seal({"step": 1, "position": [1, 1], "hint": "🙂"}, "nonce")
    assert verify_records([record]) == (True, [])
    bad_nonce = record | {"nonce": "changed"}
    bad_payload = record | {"payload": record["payload"] | {"position": [1, 2]}}
    assert not verify_audit([bad_nonce])["verified"]
    assert not verify_audit([bad_payload])["verified"]
    forged = seal(
        {
            "step": 1,
            "sender": "thief",
            "position": [6, 6],
            "action": {"type": "move", "direction": "N", "barrier": None},
        }
    )
    assert not replay_sequence([forged], profile().board_config)["verified"]


def test_artifact_grammars_roundtrip_and_serializations_are_distinct(tmp_path: Path) -> None:
    value = {"z": "שלום", "a": 0.9}
    assert pretty_bytes(value) != canonical_json(value).encode()
    assert canonical_sha256(value) != consensus_sha256(value)
    paths = write_artifacts(
        tmp_path, "game", 3, profile().object(), {"records": []}, {"verified": True}
    )
    assert {path.name for path in paths} == {
        "declaration_game.json",
        "config_game_g03.json",
        "log_game_g03.json",
        "result_game.json",
    }
    assert all(json.loads(path.read_text(encoding="utf-8")) for path in paths)
