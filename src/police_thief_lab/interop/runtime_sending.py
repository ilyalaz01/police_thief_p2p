"""Outbound turn construction and delivery methods for the peer runtime."""

from __future__ import annotations

import time

from ..models import MoveType, Position, Role
from ..presentation import TurnBanner
from ..rules import DELTAS
from ..scent import scent_model_for
from .crypto import seal
from .protocol import TurnMessage
from .runtime_models import PeerPhase, action_to_wire


class _RuntimeSendingMixin:
    """Represent RuntimeSendingMixin as one cohesive typed implementation boundary."""
    def _act_and_send(self, step: int) -> None:
        """Compute the internal act and send step used by _RuntimeSendingMixin."""
        self.phase = PeerPhase.ACTING
        observation = self._observation()
        started = time.perf_counter()
        action = self.backend.choose_action(observation)
        self.strategy_ms.append((time.perf_counter() - started) * 1000)
        if action not in observation.legal_actions:
            raise ValueError("DecisionBackend selected an illegal action")
        barrier = None
        if action.move_type is MoveType.MOVE:
            dr, dc = DELTAS[action.direction]
            self.state.position = Position(
                self.state.position.row + dr,
                self.state.position.col + dc,
            )
        elif action.move_type is MoveType.BARRIER:
            barrier = action.barrier_position
            self.state.barriers.add(barrier)
            self.state.own_barriers += 1
        self.state.own_moves += 1
        self.state.own_scent = scent_model_for(self.profile.scent_profile).advance(
            self.state.own_scent,
            self.state.position,
            self.config.board_size,
        )
        payload = {
            "step": step,
            "sender": self.role.value,
            "action": action_to_wire(action),
            "position": [self.state.position.row, self.state.position.col],
            "hint": self.hint,
        }
        record = seal(payload)
        self.records.append(record)
        claim = (
            [self.state.position.row, self.state.position.col]
            if self.role is Role.POLICE and action.move_type is MoveType.MOVE
            else None
        )
        win = None
        if self.role is Role.THIEF and self.state.own_moves >= self.profile.survival_limit:
            self.state.terminal = "survival"
            win = {"type": "survival"}
        message = TurnMessage(
            step,
            self.role.value,
            self.hint,
            {f"{p.row},{p.col}": v for p, v in self.state.own_scent},
            record["commit"],
            f"2026-08-15T00:00:{step:02d}+03:00",
            [barrier.row, barrier.col] if barrier else None,
            claim,
            self.state.pending_claim_response,
            win,
        )
        self.state.pending_claim_response = None
        if self.profile.step_numbering == "global_sequence":
            self.receiver.mark_local(step, record["commit"])
        self.roundtrip_ms.append(self.client.call("receive_turn", message.to_dict()))
        self.events.append(
            {
                "event": "sent",
                "step": step,
                "action": action_to_wire(action),
                "terminal": self.state.terminal,
                "wire": message.to_dict(),
            }
        )
        self._publish_live(TurnBanner.LOCKED)

    def _send_terminal_response(self, step: int) -> None:
        """Compute the internal send terminal response step used by _RuntimeSendingMixin."""
        payload = {
            "step": step,
            "sender": self.role.value,
            "action": None,
            "position": [self.state.position.row, self.state.position.col],
            "terminal": self.state.terminal,
            "hint": self.hint,
        }
        record = seal(payload)
        self.records.append(record)
        response = {"caught": True, "reason": self.state.terminal}
        message = TurnMessage(
            step,
            self.role.value,
            self.hint,
            {},
            record["commit"],
            f"2026-08-15T00:00:{step:02d}+03:00",
            claim_response=response,
        )
        if self.profile.step_numbering == "global_sequence":
            self.receiver.mark_local(step, record["commit"])
        self.roundtrip_ms.append(self.client.call("receive_turn", message.to_dict()))
        self.events.append({"event": "terminal_response", "step": step})
        self._publish_live(TurnBanner.LOCKED)
