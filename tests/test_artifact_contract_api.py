"""Characterization of artifact public helpers, constants, and moved AST."""

import ast
import inspect
import json
from pathlib import Path

from artifact_contract_hashes import SCHEMA_HASHES
from artifact_contract_support import _sha

from police_thief_lab.interop import artifacts


def test_public_helpers_constants_signatures_and_moved_ast_are_exact() -> None:
    assert {
        name: _sha(getattr(artifacts, name).encode()) for name in SCHEMA_HASHES
    } == SCHEMA_HASHES
    signatures = {
        "pretty_bytes": "(value: 'dict[str, Any]') -> 'bytes'",
        "canonical_sha256": "(value: 'Any') -> 'str'",
        "consensus_sha256": "(value: 'Any') -> 'str'",
        "derive_game_ids": (
            "(terms: 'dict[str, Any]', group_a: 'str', group_b: 'str') -> 'tuple[str, str]'"
        ),
        "score_sub_game": "(result: 'str', roles: 'dict[str, str]') -> 'dict[str, int]'",
        "aggregate_scores": "(score: 'dict[str, int]') -> 'dict[str, Any]'",
        "final_consensus_scope": (
            "(game_id: 'str', aggregate: 'dict[str, Any]', "
            "sub_games: 'list[dict[str, Any]]') -> 'dict[str, Any]'"
        ),
        "artifact_links": "(game_id: 'str') -> 'dict[str, str]'",
        "_hardware": "(spec: 'dict[str, Any]') -> 'dict[str, Any]'",
        "_group": "(identity: 'dict[str, Any]') -> 'dict[str, Any]'",
        "build_declaration": (
            "(game_id: 'str', game_uid: 'str', timezone: 'str', game_started_at: 'str', "
            "game_ended_at: 'str', num_sub_games: 'int', max_tokens_per_game: 'int', "
            "own: 'dict[str, Any]', opponent: 'dict[str, Any]') -> 'dict[str, Any]'"
        ),
        "build_config_artifact": (
            "(shared_terms: 'dict[str, Any]', game_id: 'str', game_uid: 'str', "
            "sub_game_number: 'int') -> 'dict[str, Any]'"
        ),
        "_ended_at": "(started_at: 'str', duration_seconds: 'float') -> 'str'",
        "build_log": (
            "(summary: 'dict[str, Any]', game_id: 'str', game_uid: 'str', group_id: 'str', "
            "opponent_group_id: 'str') -> 'dict[str, Any]'"
        ),
        "build_result": (
            "(game_id: 'str', game_uid: 'str', group_ids: 'list[str] | tuple[str, ...]', "
            "sub_games: 'list[dict[str, Any]]', aggregate_out: 'dict[str, Any]', "
            "mutual_sha256: 'str') -> 'dict[str, Any]'"
        ),
        "write_reference_v3_artifacts": (
            "(directory: 'Path', game_id: 'str', game_uid: 'str', game_number: 'int', "
            "shared_terms: 'dict[str, Any]', log_summary: 'dict[str, Any]', "
            "own_identity: 'dict[str, Any]', peer_identity: 'dict[str, Any]', "
            "sub_game: 'dict[str, Any]', aggregate_out: 'dict[str, Any]', "
            "mutual_sha256: 'str', game_started_at: 'str', game_ended_at: 'str', "
            "max_tokens_per_game: 'int' = 0) -> 'list[Path]'"
        ),
        "write_artifacts": (
            "(directory: 'Path', game_id: 'str', game_number: 'int', "
            "profile: 'dict[str, Any]', log: 'dict[str, Any]', "
            "result: 'dict[str, Any]') -> 'list[Path]'"
        ),
    }
    assert {
        name: str(inspect.signature(getattr(artifacts, name))) for name in signatures
    } == signatures
    moved = {
        "pretty_bytes",
        "canonical_sha256",
        "consensus_sha256",
        "artifact_links",
        "_hardware",
        "_group",
        "_ended_at",
    }
    nodes = {}
    paths = (Path(artifacts.__file__), Path(artifacts.__file__).with_name("artifact_encoding.py"))
    for path in (path for path in paths if path.exists()):
        for node in ast.parse(path.read_text()).body:
            if isinstance(node, ast.FunctionDef) and node.name in moved:
                nodes[node.name] = ast.dump(node, include_attributes=False)
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "LINKS_REMARK"
                for target in node.targets
            ):
                nodes["LINKS_REMARK"] = ast.dump(node, include_attributes=False)
    encoded = json.dumps(nodes, sort_keys=True, separators=(",", ":")).encode()
    assert (len(nodes), _sha(encoded)) == (
        8,
        "9fbc2558bc35ede430993a685c4d8abb7cd0763be0180df2b0d3e2fd26f7cfdf",
    )
