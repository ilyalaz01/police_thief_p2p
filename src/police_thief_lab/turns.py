"""Isolated reference-v3 alternating turn and terminal semantics."""

from __future__ import annotations

from dataclasses import replace

from .models import GameConfig, Role, TerminalReason, WorldState
from .rules import score_for, thief_boxed_in


class ReferenceV3Alternating:
    """Thief-first serial cadence; there is no joint-action resolution."""

    @staticmethod
    def first_role() -> Role:
        """Return the owner of the initial turn token."""
        return Role.THIEF

    @staticmethod
    def next_role(role: Role) -> Role:
        """Pass the turn token to the other role."""
        return Role.POLICE if role is Role.THIEF else Role.THIEF

    @staticmethod
    def settle_after_action(state: WorldState, actor: Role, config: GameConfig) -> WorldState:
        """Apply mandatory capture precedence and reference claim/survival timing."""
        barrier_cells = {barrier.position for barrier in state.barriers}
        if state.thief_position in barrier_cells:
            return _terminal(state, TerminalReason.BARRIER_ON_THIEF)
        if thief_boxed_in(state, config):
            return _terminal(state, TerminalReason.THIEF_BOXED_IN)
        # A Police action creates the reference post-action capture claim. A Thief
        # entering that cell is not resolved until Police next owns and acts on the token.
        if actor is Role.POLICE and state.police_position == state.thief_position:
            return _terminal(state, TerminalReason.POLICE_CAPTURE)
        if actor is Role.THIEF and state.thief_moves >= config.survival_threshold:
            return _terminal(state, TerminalReason.THIEF_SURVIVED)
        return replace(state, next_role=ReferenceV3Alternating.next_role(actor))


def _terminal(state: WorldState, reason: TerminalReason) -> WorldState:
    return replace(state, terminal_reason=reason, score=score_for(reason))
