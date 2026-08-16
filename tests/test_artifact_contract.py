"""Characterization of schema 1.1 artifact bytes and consensus contracts."""
# ruff: noqa: E501 -- fixed hashes and schema inputs are clearer as single records.

import ast
import hashlib
import inspect
import json
from pathlib import Path

from police_thief_lab.interop import artifacts
from police_thief_lab.interop.artifacts import (
    LINKS_REMARK,
    aggregate_scores,
    artifact_links,
    build_config_artifact,
    build_declaration,
    build_log,
    build_result,
    canonical_sha256,
    consensus_sha256,
    derive_game_ids,
    final_consensus_scope,
    pretty_bytes,
    score_sub_game,
    write_artifacts,
    write_reference_v3_artifacts,
)

SCHEMA_HASHES = {
    "SCHEMA_VERSION": "b05e244762b1e472be89a93800cc3ee326743cecb55984bf12813addb8de66d0",
    "DEFAULT_TIMEZONE": "767f41f547937e73856a64ae5abc126fab75c2fe4fa6161c59de416a8419cc73",
    "SCHEMA_DECLARATION": "775d4ffdba6a5c5aaa17462473af2201a3e3ac9a2c3758c8e8804815d2a5eaad",
    "SCHEMA_CONFIG": "3caf13e6de1913fbb6aff074c215611bf730184481c680f4d176f3a8d59e022b",
    "SCHEMA_LOG": "7b52d6ce43caa59e24e26f500b3199c6ab16f22b376a8a04fa2f0817274728b3",
    "SCHEMA_RESULT": "9d706d485c16033b0d62b1eb221e65b852168745dfa88a1b9a491a229ee1782e",
    "LINKS_REMARK": "ac09408f8e04aaee502523a06ba49fec1dbeb5beaa9d13a294e9241920d1d7b2",
}
OBJECT_HASHES = ["01ab9bf121d11c06bacaf9db589a793282b171324c2dff9395a8b4740bf54cd0", "d9cf2e523fb5faf6b5d08d9c2fe5908baf3938bb194178ac7924042dd8e51311", "4c6dee80696990886cd6fc888e891776518f5135ca80d950fd6c9eedb0d00112", "a84671f01acd8fc7e75ea41127f436f6fe5826eef4bca83dcaaa04cca1cbceee"]
PRETTY_HASHES = ["bcddd47dce7dba55880f67f85ff79d02f080f198890edece359902659cdd0d03", "c0b0afcba1e62370c3d5624b3671e825f8aa5967f40ee3fda8322f081dd24881", "c004244f2933eddb252b783f5f4e776264b4e1abdd9f27c6b5c7dd768a97eca1", "4e9012aa5d6bc078bf367fd8d140644c3cf01f157a1435be26975ebf1f208164"]
REFERENCE_FILES = [("declaration_game.json", PRETTY_HASHES[0]), ("config_game_g01.json", PRETTY_HASHES[1]), ("log_game_g01.json", PRETTY_HASHES[2]), ("result_game.json", PRETTY_HASHES[3])]
LOCAL_FILES = [("declaration_game.json", "71d2edca2b6f239bdba387c7fe3348ee66be702421670608fcd5a5e1c28f47e8"), ("config_game_g01.json", "66e1743da003d1636d160b4ade9bf25a7b6f1046478de483bd6c9ca4c6dd5184"), ("log_game_g01.json", "e933c34bc23c39d19b56988ff04b10bebdbb33619d7fa2d9108969c1771b8a47"), ("result_game.json", "e67a41ef2f45ecd3bece62a63c4748d0fd1f52ac6f8449648fc04d390d36233f")]


def _inputs() -> tuple[dict, ...]:
    own = {"group_id": "alpha", "group_name": "Alpha", "members": ["id-1"], "repos": {"cop": "repo-c", "thief": "repo-t"}, "mcp_servers": {"cop": "https://alpha.example/mcp"}, "llm_model": "deterministic-python", "spec": {"cpu_type": "cpu", "cpu_freq_mhz": 1, "cpu_cores": 2, "ram_gb": 3, "gpu_type": None, "vram_gb": 0}}
    peer = own | {"group_id": "beta", "group_name": "Beta", "mcp_servers": {"cop": "https://beta.example/mcp"}}
    terms = {"board_size": 7, "setting": "ירושלים🙂"}
    records = [{"payload": {"step": 1}, "nonce": "n", "commit": "c"}]
    summary = {"records": records, "sub_game_number": 1, "role": "cop", "result": "capture", "winner": "cop", "steps": 1, "started_at": "2026-08-15T00:00:00+00:00", "duration_seconds": 2.5, "tokens_total": 0, "audit": {"passed": True, "verified_steps": 1, "failed_steps": []}}
    sub = {"sub_game_number": 1, "roles": {"alpha": "cop", "beta": "thief"}, "result": "capture", "winner_group": "alpha", "score": {"alpha": 20, "beta": 5}, "tie": True, "tokens": {"alpha": 3}, "audit": {"log_verified": True}, "started_at": "excluded", "github_commit": {"alpha": "x"}}
    aggregate = {"total_score": {"alpha": 20, "beta": 5}, "sub_games_won": {"alpha": 1, "beta": 0}, "ties": 0, "winner_group": "alpha", "series_tie": False}
    return own, peer, terms, records, summary, sub, aggregate


def _objects() -> list[dict]:
    own, peer, terms, _records, summary, sub, aggregate = _inputs()
    return [build_declaration("game", "uid", "Asia/Jerusalem", "start", "end", 1, 0, own, peer), build_config_artifact(terms, "game", "uid", 1), build_log(summary, "game", "uid", "alpha", "beta"), build_result("game", "uid", ["alpha", "beta"], [sub], aggregate, "agreed-hash")]


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def test_public_helpers_constants_signatures_and_moved_ast_are_exact() -> None:
    assert {name: _sha(getattr(artifacts, name).encode()) for name in SCHEMA_HASHES} == SCHEMA_HASHES
    signatures = {"pretty_bytes": "(value: 'dict[str, Any]') -> 'bytes'", "canonical_sha256": "(value: 'Any') -> 'str'", "consensus_sha256": "(value: 'Any') -> 'str'", "derive_game_ids": "(terms: 'dict[str, Any]', group_a: 'str', group_b: 'str') -> 'tuple[str, str]'", "score_sub_game": "(result: 'str', roles: 'dict[str, str]') -> 'dict[str, int]'", "aggregate_scores": "(score: 'dict[str, int]') -> 'dict[str, Any]'", "final_consensus_scope": "(game_id: 'str', aggregate: 'dict[str, Any]', sub_games: 'list[dict[str, Any]]') -> 'dict[str, Any]'", "artifact_links": "(game_id: 'str') -> 'dict[str, str]'", "_hardware": "(spec: 'dict[str, Any]') -> 'dict[str, Any]'", "_group": "(identity: 'dict[str, Any]') -> 'dict[str, Any]'", "build_declaration": "(game_id: 'str', game_uid: 'str', timezone: 'str', game_started_at: 'str', game_ended_at: 'str', num_sub_games: 'int', max_tokens_per_game: 'int', own: 'dict[str, Any]', opponent: 'dict[str, Any]') -> 'dict[str, Any]'", "build_config_artifact": "(shared_terms: 'dict[str, Any]', game_id: 'str', game_uid: 'str', sub_game_number: 'int') -> 'dict[str, Any]'", "_ended_at": "(started_at: 'str', duration_seconds: 'float') -> 'str'", "build_log": "(summary: 'dict[str, Any]', game_id: 'str', game_uid: 'str', group_id: 'str', opponent_group_id: 'str') -> 'dict[str, Any]'", "build_result": "(game_id: 'str', game_uid: 'str', group_ids: 'list[str] | tuple[str, ...]', sub_games: 'list[dict[str, Any]]', aggregate_out: 'dict[str, Any]', mutual_sha256: 'str') -> 'dict[str, Any]'", "write_reference_v3_artifacts": "(directory: 'Path', game_id: 'str', game_uid: 'str', game_number: 'int', shared_terms: 'dict[str, Any]', log_summary: 'dict[str, Any]', own_identity: 'dict[str, Any]', peer_identity: 'dict[str, Any]', sub_game: 'dict[str, Any]', aggregate_out: 'dict[str, Any]', mutual_sha256: 'str', game_started_at: 'str', game_ended_at: 'str', max_tokens_per_game: 'int' = 0) -> 'list[Path]'", "write_artifacts": "(directory: 'Path', game_id: 'str', game_number: 'int', profile: 'dict[str, Any]', log: 'dict[str, Any]', result: 'dict[str, Any]') -> 'list[Path]'"}
    assert {name: str(inspect.signature(getattr(artifacts, name))) for name in signatures} == signatures
    moved = {"pretty_bytes", "canonical_sha256", "consensus_sha256", "artifact_links", "_hardware", "_group", "_ended_at"}
    nodes = {}
    paths = (Path(artifacts.__file__), Path(artifacts.__file__).with_name("artifact_encoding.py"))
    for path in (path for path in paths if path.exists()):
        for node in ast.parse(path.read_text()).body:
            if isinstance(node, ast.FunctionDef) and node.name in moved:
                nodes[node.name] = ast.dump(node, include_attributes=False)
            if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "LINKS_REMARK" for target in node.targets):
                nodes["LINKS_REMARK"] = ast.dump(node, include_attributes=False)
    encoded = json.dumps(nodes, sort_keys=True, separators=(",", ":")).encode()
    assert (len(nodes), _sha(encoded)) == (8, "9fbc2558bc35ede430993a685c4d8abb7cd0763be0180df2b0d3e2fd26f7cfdf")


def test_builder_object_pretty_canonical_and_consensus_bytes_are_exact() -> None:
    objects = _objects()
    assert [_sha(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()) for value in objects] == OBJECT_HASHES
    assert [_sha(pretty_bytes(value)) for value in objects] == PRETTY_HASHES
    terms, sub, aggregate = _inputs()[2], _inputs()[5], _inputs()[6]
    assert artifacts.canonical_json(terms) == '{"board_size":7,"setting":"ירושלים🙂"}'
    assert canonical_sha256(terms) == "bddf21fe4533895b25d06a8785cca7bc49938243d100549c4dd88d9167dfd1b3"
    scope = final_consensus_scope("game", aggregate, [sub])
    assert json.dumps(scope, sort_keys=True, ensure_ascii=False) == '{"aggregate": {"series_tie": false, "sub_games_won": {"alpha": 1, "beta": 0}, "ties": 0, "total_score": {"alpha": 20, "beta": 5}, "winner_group": "alpha"}, "game_id": "game", "sub_games": [{"result": "capture", "roles": {"alpha": "cop", "beta": "thief"}, "score": {"alpha": 20, "beta": 5}, "sub_game_number": 1, "winner_group": "alpha"}]}'
    assert consensus_sha256(scope) == "55bdb77b8be204338518d6da3ce9a67e42d9868d2a50ee0d525a3d2756061178"


def test_writers_names_order_and_bytes_are_exact(tmp_path: Path) -> None:
    own, peer, terms, records, summary, sub, aggregate = _inputs()
    reference = write_reference_v3_artifacts(tmp_path / "ref", "game", "uid", 1, terms, summary, own, peer, sub, aggregate, "agreed-hash", "start", "end")
    local = write_artifacts(tmp_path / "local", "game", 1, terms, {"records": records}, {"verified": True})
    assert [(path.name, _sha(path.read_bytes())) for path in reference] == REFERENCE_FILES
    assert [(path.name, _sha(path.read_bytes())) for path in local] == LOCAL_FILES


def test_ids_scoring_aggregation_tie_scope_and_fallback_are_exact() -> None:
    terms, sub, aggregate = _inputs()[2], _inputs()[5], _inputs()[6]
    assert derive_game_ids(terms, "beta", "alpha") == ("alpha-vs-beta", "9715936d-696a-8856-ff12-1b57c46c9df3")
    assert score_sub_game("capture", {"alpha": "police", "beta": "thief"}) == {"alpha": 20, "beta": 5}
    assert score_sub_game("survival", {"alpha": "police", "beta": "thief"}) == {"alpha": 5, "beta": 10}
    assert score_sub_game("other", {"alpha": "police"}) == {"alpha": 0}
    assert aggregate_scores({"alpha": 5, "beta": 5}) == {"total_score": {"alpha": 5, "beta": 5}, "sub_games_won": {"alpha": 0, "beta": 0}, "ties": 1, "winner_group": None, "series_tie": True}
    assert aggregate_scores({"alpha": 20, "beta": 5})["winner_group"] == "alpha"
    result = build_result("game", "uid", ["alpha", "beta"], [sub], aggregate, "hash")
    assert result["sub_games"][0]["tie"] is True
    assert set(sub) - set(final_consensus_scope("game", aggregate, [sub])["sub_games"][0]) == {"tie", "tokens", "audit", "started_at", "github_commit"}
    assert artifacts._ended_at("2026-01-01T00:00:00+00:00", 2.5) == "2026-01-01T00:00:02.500000+00:00"
    assert artifacts._ended_at("invalid", 2.5) == "invalid"
    assert artifacts._ended_at(None, 2.5) is None
    assert artifact_links("game")["_remark"] == LINKS_REMARK
