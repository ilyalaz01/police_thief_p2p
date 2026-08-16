"""Negotiation and inbound lifecycle methods for the peer runtime."""

from __future__ import annotations

import queue
import time
from typing import Any

from ..models import Role
from .protocol import TurnMessage
from .runtime_models import (
    DeadlineTracker,
    PeerPhase,
    _position,
    require_real_team_git_commit,
)


class _RuntimeLifecycleMixin:
    def _diagnostic(self, event: str, **extra: Any) -> None:
        self.events.append(
            {
                "event": event,
                "role": self.role.value,
                "phase": self.phase.value,
                "local_step": self._next_outbound_step - 1,
                "last_received_sender_step": self.receiver.next_step - 1,
                "opponent_url": self.opponent_url,
                "connection_status": extra.pop("connection_status", "connected"),
                "retry_count": max(0, self.client.last_attempts - 1),
                "config_sha256": self.profile.sha256,
                "game_id": extra.pop("game_id", None),
                "terminal_reason": self.state.terminal,
                **extra,
            }
        )

    def _negotiate(self) -> None:
        self.phase = PeerPhase.NEGOTIATING
        self.roundtrip_ms.append(
            self.client.call("negotiate", self.profile.agreement(self.role.value, self.identity))
        )
        try:
            remote = self.inboxes.agreements.get(timeout=self.profile.timeouts["connect"])
        except queue.Empty as exc:
            raise TimeoutError("negotiation deadline") from exc
        self.profile.verify_agreement(remote)
        self.peer_identity = remote.get("identity", {})
        if self.real_team:
            require_real_team_git_commit(self.peer_identity.get("github_commit"), "peer")
        self._diagnostic("negotiated")

    def _receive_and_maybe_act(self) -> None:
        self.phase = PeerPhase.WAITING
        deadline = DeadlineTracker(self.profile.timeouts["turn"])
        ready: list[TurnMessage] = []
        while not ready:
            try:
                raw = self.inboxes.turns.get(timeout=deadline.remaining())
            except queue.Empty:
                self.state.terminal = "timeout"
                self._diagnostic("timeout", connection_status="timed_out", remaining_deadline=0.0)
                return
            ready = self.receiver.offer(raw)
        for message in ready:
            began = time.perf_counter()
            self._apply_inbound(message)
            if self.state.terminal is None:
                self._act_and_send(self._next_outbound())
            self.turn_ms.append((time.perf_counter() - began) * 1000)

    def _apply_inbound(self, message: TurnMessage) -> None:
        if message.sender == self.role.value:
            raise ValueError("peer sent a turn under our role")
        self.state.opponent_scent = tuple(
            sorted(
                (_position([int(part) for part in key.split(",")]), value)
                for key, value in message.smell_grid.items()
            )
        )
        if message.barrier_placed is not None:
            barrier = _position(message.barrier_placed)
            self.state.barriers.add(barrier)
            if self.role is Role.THIEF and barrier == self.state.position:
                self.state.terminal = "barrier_on_thief"
            elif self.role is Role.THIEF and self._boxed_in():
                self.state.terminal = "thief_boxed_in"
        if self.role is Role.THIEF and message.capture_claim is not None:
            caught = _position(message.capture_claim) == self.state.position
            if caught:
                self.state.terminal = "police_capture"
            else:
                self.state.pending_claim_response = {
                    "claim": message.capture_claim,
                    "caught": False,
                }
        if message.claim_response and message.claim_response.get("caught"):
            self.state.terminal = message.claim_response.get("reason", "police_capture")
        if message.win_claim:
            self.state.terminal = message.win_claim.get("type", "survival")
        self.events.append(
            {
                "event": "received",
                "step": message.step,
                "terminal": self.state.terminal,
                "wire": message.to_dict(),
            }
        )
        if self.state.terminal and self.role is Role.THIEF and not message.claim_response:
            self._send_terminal_response(self._next_outbound())
