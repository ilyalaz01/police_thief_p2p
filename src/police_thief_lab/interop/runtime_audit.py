"""Audit and replay completion methods for the peer runtime."""

from __future__ import annotations

import queue
import time
from typing import Any

from .artifacts import consensus_sha256, derive_game_ids, write_artifacts
from .replay import replay_sequence, verify_audit
from .runtime_models import PeerPhase, _audit_result


class _RuntimeAuditMixin:
    """Represent RuntimeAuditMixin as one cohesive typed implementation boundary."""
    def _audit_and_finish(self) -> dict[str, Any]:
        """Compute the internal audit and finish step used by _RuntimeAuditMixin."""
        self.phase = PeerPhase.AUDITING
        audit_started = time.perf_counter()
        payload = {
            "sender": self.role.value,
            "records": self.records,
            "result_claim": self.state.terminal,
        }
        try:
            self.roundtrip_ms.append(
                self.client.call("submit_audit", payload, self.profile.timeouts["audit"])
            )
        except TimeoutError:
            # Reference-compatible best effort: the peer may exit after its audit
            # already reached this inbox while our response acknowledgement was lost.
            self.events.append({"event": "audit_send_unacknowledged"})
        try:
            remote = self.inboxes.audits.get(timeout=self.profile.timeouts["audit"])
        except queue.Empty as exc:
            raise TimeoutError("audit deadline") from exc
        local_check = verify_audit(self.records)
        remote_check = verify_audit(remote["records"])
        claims_match = _audit_result(remote["result_claim"]) == _audit_result(
            self.state.terminal
        )
        verified = local_check["verified"] and remote_check["verified"] and claims_match
        audit_ms = (time.perf_counter() - audit_started) * 1000
        self.phase = PeerPhase.VERIFIED if verified else PeerPhase.FAILED
        peer_group = self.peer_identity.get("group_id", "unknown-peer")
        game_id, game_uid = derive_game_ids(
            self.profile.reference_terms(),
            self.identity["group_id"],
            peer_group,
        )
        outcome = {
            "game_id": game_id,
            "outcome": _audit_result(self.state.terminal),
            "verified": verified,
            "profile": self.profile.artifact_profile,
        }
        outcome["mutual_agreement"] = consensus_sha256(outcome.copy())
        remote_records = [
            dict(record, _audit_sender=remote["sender"])
            for record in remote["records"]
        ]
        combined = sorted(
            self.records + remote_records,
            key=lambda record: record["payload"]["step"],
        )
        replay_started = time.perf_counter()
        replay_check = replay_sequence(combined, self.profile.board_config)
        replay_ms = (time.perf_counter() - replay_started) * 1000
        if self.profile.artifact_profile == "reference-v3-artifact-1.1":
            paths = self._write_reference_artifacts(
                game_id,
                game_uid,
                peer_group,
                combined,
                verified,
            )
        else:
            paths = write_artifacts(
                self.artifact_dir,
                game_id,
                1,
                self.profile.object(),
                {"records": combined, "audit": remote_check, "events": self.events},
                outcome,
            )
        return {
            "ok": verified and replay_check["verified"],
            "role": self.role.value,
            "phase": self.phase.value,
            "outcome": self.state.terminal,
            "config_sha256": self.profile.sha256,
            "records": len(combined),
            "duplicates": self.receiver.absorbed,
            "audit": remote_check,
            "replay": replay_check,
            "artifacts": [str(path) for path in paths],
            "metrics": {
                "strategy_ms": self.strategy_ms,
                "mcp_roundtrip_ms": self.roundtrip_ms,
                "turn_ms": self.turn_ms,
                "audit_ms": audit_ms,
                "replay_ms": replay_ms,
            },
            "events": self.events,
        }
