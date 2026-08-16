"""Audit, commitment, and official artifact operations exposed through the SDK."""

from ..interop.artifact_encoding import (
    artifact_links,
    canonical_sha256,
    consensus_sha256,
    pretty_bytes,
)
from ..interop.artifacts import (
    aggregate_scores,
    build_config_artifact,
    build_declaration,
    build_log,
    build_result,
    derive_game_ids,
    final_consensus_scope,
    score_sub_game,
    write_artifacts,
    write_reference_v3_artifacts,
)
from ..interop.crypto import canonical_json, hcommit, seal, verify_records
from ..interop.replay import position, replay_sequence, verify_audit


class ArtifactsSDK:
    """Stable access to byte scopes, audit/replay, scoring, and schema 1.1 builders."""

    aggregate_scores = staticmethod(aggregate_scores)
    artifact_links = staticmethod(artifact_links)
    build_config_artifact = staticmethod(build_config_artifact)
    build_declaration = staticmethod(build_declaration)
    build_log = staticmethod(build_log)
    build_result = staticmethod(build_result)
    canonical_json = staticmethod(canonical_json)
    canonical_sha256 = staticmethod(canonical_sha256)
    consensus_sha256 = staticmethod(consensus_sha256)
    derive_game_ids = staticmethod(derive_game_ids)
    final_consensus_scope = staticmethod(final_consensus_scope)
    hcommit = staticmethod(hcommit)
    position = staticmethod(position)
    pretty_bytes = staticmethod(pretty_bytes)
    replay_sequence = staticmethod(replay_sequence)
    score_sub_game = staticmethod(score_sub_game)
    seal = staticmethod(seal)
    verify_audit = staticmethod(verify_audit)
    verify_records = staticmethod(verify_records)
    write_artifacts = staticmethod(write_artifacts)
    write_reference_v3_artifacts = staticmethod(write_reference_v3_artifacts)
