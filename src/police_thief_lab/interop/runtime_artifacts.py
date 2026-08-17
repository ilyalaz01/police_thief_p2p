"""Reference schema 1.1 artifact assembly for the peer runtime."""

from __future__ import annotations

from datetime import UTC, datetime

from ..models import Role
from .artifacts import (
    aggregate_scores,
    consensus_sha256,
    final_consensus_scope,
    score_sub_game,
    write_reference_v3_artifacts,
)
from .runtime_models import UNRESOLVED_GIT_COMMIT, _audit_result


class _RuntimeArtifactsMixin:
    """Represent RuntimeArtifactsMixin as one cohesive typed implementation boundary."""
    def _write_reference_artifacts(
        self,
        game_id,
        game_uid,
        peer_group,
        combined,
        verified,
    ):
        """Compute the internal write reference artifacts step used by _RuntimeArtifactsMixin."""
        winner = "thief" if _audit_result(self.state.terminal) == "survival" else "police"
        winner_group = self.identity["group_id"] if self.role.value == winner else peer_group
        role_groups = {
            self.identity["group_id"]: self.role.value,
            peer_group: "thief" if self.role is Role.POLICE else "police",
        }
        score = score_sub_game(_audit_result(self.state.terminal), role_groups)
        aggregate = aggregate_scores(score)
        ended_at = datetime.now(UTC)
        sub_game = self._sub_game(
            game_id,
            peer_group,
            role_groups,
            winner_group,
            score,
            ended_at,
            verified,
        )
        mutual_sha = consensus_sha256(final_consensus_scope(game_id, aggregate, [sub_game]))
        log_summary = self._log_summary(combined, winner, ended_at, verified)
        return write_reference_v3_artifacts(
            self.artifact_dir,
            game_id,
            game_uid,
            1,
            self.profile.reference_terms(),
            log_summary,
            self.identity,
            self.peer_identity,
            sub_game,
            aggregate,
            mutual_sha,
            self.started_at.isoformat(),
            ended_at.isoformat(),
        )

    def _sub_game(
        self,
        game_id,
        peer_group,
        role_groups,
        winner_group,
        score,
        ended_at,
        verified,
    ):
        """Compute the internal sub game step used by _RuntimeArtifactsMixin."""
        return {
            "sub_game_number": 1,
            "roles": role_groups,
            "started_at": self.started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "result": _audit_result(self.state.terminal),
            "winner_group": winner_group,
            "github_commit": {
                self.identity["group_id"]: self.git_commit,
                peer_group: self.peer_identity.get(
                    "github_commit",
                    UNRESOLVED_GIT_COMMIT,
                ),
            },
            "tokens": dict.fromkeys(role_groups, 0),
            "score": score,
            "log_files": {
                group: f"{group}/log_{game_id}_g01.json" for group in role_groups
            },
            "audit": {"log_verified": verified, "tampered": not verified},
        }

    def _log_summary(self, combined, winner, ended_at, verified):
        """Compute the internal log summary step used by _RuntimeArtifactsMixin."""
        return {
            "records": combined,
            "sub_game_number": 1,
            "role": self.role.value,
            "result": _audit_result(self.state.terminal),
            "winner": winner,
            "steps": len(combined),
            "started_at": self.started_at.isoformat(),
            "duration_seconds": (ended_at - self.started_at).total_seconds(),
            "tokens_total": 0,
            "audit": {
                "passed": verified,
                "verified_steps": len(combined),
                "failed_steps": [] if verified else ["audit_or_claim"],
            },
        }
