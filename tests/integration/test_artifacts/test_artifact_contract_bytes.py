"""Characterization of artifact bytes, writers, scoring, and consensus."""

import json
from pathlib import Path

from police_thief_lab.interop import artifacts
from police_thief_lab.interop.artifacts import (
    LINKS_REMARK,
    aggregate_scores,
    artifact_links,
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
from tests.support.artifact_contract_hashes import (
    LOCAL_FILES,
    OBJECT_HASHES,
    PRETTY_HASHES,
    REFERENCE_FILES,
)
from tests.support.artifact_contract_support import _inputs, _objects, _sha


def test_builder_object_pretty_canonical_and_consensus_bytes_are_exact() -> None:
    objects = _objects()
    assert [
        _sha(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode())
        for value in objects
    ] == OBJECT_HASHES
    assert [_sha(pretty_bytes(value)) for value in objects] == PRETTY_HASHES
    terms, sub, aggregate = _inputs()[2], _inputs()[5], _inputs()[6]
    assert artifacts.canonical_json(terms) == '{"board_size":7,"setting":"ירושלים🙂"}'
    assert (
        canonical_sha256(terms)
        == "bddf21fe4533895b25d06a8785cca7bc49938243d100549c4dd88d9167dfd1b3"
    )
    scope = final_consensus_scope("game", aggregate, [sub])
    assert (
        json.dumps(scope, sort_keys=True, ensure_ascii=False)
        == '{"aggregate": {"series_tie": false, "sub_games_won": '
        '{"alpha": 1, "beta": 0}, "ties": 0, "total_score": '
        '{"alpha": 20, "beta": 5}, "winner_group": "alpha"}, '
        '"game_id": "game", "sub_games": [{"result": "capture", '
        '"roles": {"alpha": "cop", "beta": "thief"}, "score": '
        '{"alpha": 20, "beta": 5}, "sub_game_number": 1, '
        '"winner_group": "alpha"}]}'
    )
    assert (
        consensus_sha256(scope)
        == "55bdb77b8be204338518d6da3ce9a67e42d9868d2a50ee0d525a3d2756061178"
    )


def test_writers_names_order_and_bytes_are_exact(tmp_path: Path) -> None:
    own, peer, terms, records, summary, sub, aggregate = _inputs()
    reference = write_reference_v3_artifacts(
        tmp_path / "ref",
        "game",
        "uid",
        1,
        terms,
        summary,
        own,
        peer,
        sub,
        aggregate,
        "agreed-hash",
        "start",
        "end",
    )
    local = write_artifacts(
        tmp_path / "local", "game", 1, terms, {"records": records}, {"verified": True}
    )
    assert [(path.name, _sha(path.read_bytes())) for path in reference] == REFERENCE_FILES
    assert [(path.name, _sha(path.read_bytes())) for path in local] == LOCAL_FILES


def test_ids_scoring_aggregation_tie_scope_and_fallback_are_exact() -> None:
    terms, sub, aggregate = _inputs()[2], _inputs()[5], _inputs()[6]
    assert derive_game_ids(terms, "beta", "alpha") == (
        "alpha-vs-beta",
        "9715936d-696a-8856-ff12-1b57c46c9df3",
    )
    assert score_sub_game("capture", {"alpha": "police", "beta": "thief"}) == {
        "alpha": 20,
        "beta": 5,
    }
    assert score_sub_game("survival", {"alpha": "police", "beta": "thief"}) == {
        "alpha": 5,
        "beta": 10,
    }
    assert score_sub_game("other", {"alpha": "police"}) == {"alpha": 0}
    assert aggregate_scores({"alpha": 5, "beta": 5}) == {
        "total_score": {"alpha": 5, "beta": 5},
        "sub_games_won": {"alpha": 0, "beta": 0},
        "ties": 1,
        "winner_group": None,
        "series_tie": True,
    }
    assert aggregate_scores({"alpha": 20, "beta": 5})["winner_group"] == "alpha"
    result = build_result("game", "uid", ["alpha", "beta"], [sub], aggregate, "hash")
    assert result["sub_games"][0]["tie"] is True
    assert set(sub) - set(final_consensus_scope("game", aggregate, [sub])["sub_games"][0]) == {
        "tie",
        "tokens",
        "audit",
        "started_at",
        "github_commit",
    }
    assert (
        artifacts._ended_at("2026-01-01T00:00:00+00:00", 2.5) == "2026-01-01T00:00:02.500000+00:00"
    )
    assert artifacts._ended_at("invalid", 2.5) == "invalid"
    assert artifacts._ended_at(None, 2.5) is None
    assert artifact_links("game")["_remark"] == LINKS_REMARK
