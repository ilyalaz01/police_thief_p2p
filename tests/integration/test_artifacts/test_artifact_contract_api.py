"""Characterization of artifact public helpers, constants, and moved AST."""

import ast
import inspect
import json
from pathlib import Path

from police_thief_lab.interop import artifacts
from tests.support.artifact_contract_hashes import SCHEMA_HASHES
from tests.support.artifact_contract_support import _sha


def _stable_ast_dump(value: object) -> str:
    """Match Python 3.13's empty-field-neutral AST representation on 3.11+."""
    if isinstance(value, ast.AST):
        values = list(ast.iter_fields(value))
        if isinstance(value, ast.FunctionDef) and value.body:
            first = value.body[0]
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                values = [
                    (name, field_value[1:] if name == "body" else field_value)
                    for name, field_value in values
                ]
        fields = (
            f"{name}={_stable_ast_dump(field_value)}"
            for name, field_value in values
            if field_value is not None and field_value != []
        )
        return f"{type(value).__name__}({', '.join(fields)})"
    if isinstance(value, list):
        return f"[{', '.join(_stable_ast_dump(item) for item in value)}]"
    return repr(value)


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
        for node in ast.parse(path.read_text(encoding="utf-8")).body:
            if isinstance(node, ast.FunctionDef) and node.name in moved:
                nodes[node.name] = _stable_ast_dump(node)
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "LINKS_REMARK"
                for target in node.targets
            ):
                nodes["LINKS_REMARK"] = _stable_ast_dump(node)
    encoded = json.dumps(nodes, sort_keys=True, separators=(",", ":")).encode()
    assert (len(nodes), _sha(encoded)) == (
        8,
        "9fbc2558bc35ede430993a685c4d8abb7cd0763be0180df2b0d3e2fd26f7cfdf",
    )
