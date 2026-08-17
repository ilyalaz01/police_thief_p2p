"""Explicit byte-locked Phase 4A negotiated match profile."""

from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import asdict, dataclass, field
from typing import Any

from .crypto import hcommit


@dataclass(frozen=True, slots=True)
class MatchProfile:
    """Represent MatchProfile as one cohesive typed implementation boundary."""
    board_config: dict[str, Any]
    coordinate_convention: str = "row_col_zero_based"
    turn_profile: str = "reference-v3 alternating, Thief first"
    scent_profile: str = "subtractive_chebyshev_v1"
    barrier_placement_profile: str = "ADJACENT_ONLY"
    survival_limit: int = 35
    move_limit: int = 35
    timeouts: dict[str, float] = field(
        default_factory=lambda: {"connect": 10.0, "turn": 2.0, "audit": 5.0, "retry": 0.05}
    )
    artifact_profile: str = "phase4a-localhost-v1"
    artifact_schema: str = "phase4a-1.0"
    consensus_scope: str = "phase4a_symmetric_outcome_without_tie"
    setting: str = "phase4a-localhost"
    minimum_center_intensity: float = 0.3
    step_numbering: str = "global_sequence"

    def object(self) -> dict[str, Any]:
        """Perform object through the documented MatchProfile contract."""
        return asdict(self)

    def bytes(self) -> bytes:
        """Perform bytes through the documented MatchProfile contract."""
        return json.dumps(self.object(), ensure_ascii=False, indent=2).encode("utf-8")

    @property
    def sha256(self) -> str:
        """Perform sha256 through the documented MatchProfile contract."""
        return hashlib.sha256(self.bytes()).hexdigest()

    def reference_terms(self) -> dict[str, Any]:
        """Return the flat 14-key agreement understood by reference v3."""
        return {
            "board_size": self.board_config["board_size"],
            "smell_grid_size": 5,
            "decay_per_step": 0.1,
            "emit_intensity": 0.9,
            "min_center_intensity": self.minimum_center_intensity,
            "max_steps": self.move_limit,
            "barriers_max": self.board_config.get("barrier_quota", 14),
            "setting": self.setting,
            "hint_max_words": 15,
            "axis_origin_corner": "top-left",
            "axis_start_index": 0,
            "thief_start": self.board_config["thief_start"],
            "cop_start": self.board_config["police_start"],
            "num_games": 1,
        }

    def agreement(self, sender: str, identity: dict[str, Any] | None = None) -> dict[str, Any]:
        """Perform agreement through the documented MatchProfile contract."""
        nonce = secrets.token_hex(16)
        terms = self.reference_terms()
        return {
            "terms": terms,
            "nonce": nonce,
            "signature": hcommit(terms, nonce),
            "identity": (identity or {
                "group_id": f"local-{sender}",
                "group_name": f"Local {sender.title()}",
                "members": [],
                "repos": {"cop": "local-unpublished", "thief": "local-unpublished"},
                "mcp_servers": {},
                "llm_model": "deterministic-python",
                "spec": {},
            }) | {
                "phase4a_profile": self.object(),
                "config_sha256": self.sha256,
                "config_bytes_hex": self.bytes().hex(),
                "artifact_consensus_scope": self.consensus_scope,
            },
        }

    def verify_agreement(self, message: dict[str, Any]) -> None:
        """Verify and report agreement under the documented MatchProfile contract."""
        if message["terms"] != self.reference_terms():
            raise ValueError("mandatory negotiated terms mismatch")
        if hcommit(message["terms"], message["nonce"]) != message["signature"]:
            raise ValueError("invalid negotiation signature")
        identity = message.get("identity", {})
        # Omission is compatible with the unmodified reference. Phase 4A peers
        # advertise the stronger byte lock and must match exactly when present.
        if "config_bytes_hex" in identity:
            if bytes.fromhex(identity["config_bytes_hex"]) != self.bytes():
                raise ValueError("shared config is not byte-identical")
            if (
                identity.get("phase4a_profile") != self.object()
                or identity.get("config_sha256") != self.sha256
            ):
                raise ValueError("mandatory negotiated profile mismatch")
