"""Independent-process Phase 4A peer state machine."""

from __future__ import annotations

import json
import queue
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ..models import (
    Action,
    Barrier,
    BarrierPlacementMode,
    Direction,
    GameConfig,
    MoveType,
    Observation,
    Position,
    Role,
    RoleLocalState,
)
from ..policies.baselines import RandomLegalThief
from ..policies.tactical import ScentTacticalPolice
from ..rules import DELTAS
from ..scent import scent_model_for
from .artifacts import (
    aggregate_scores,
    consensus_sha256,
    derive_game_ids,
    final_consensus_scope,
    score_sub_game,
    write_artifacts,
    write_reference_v3_artifacts,
)
from .crypto import seal
from .network import redact_url
from .profile import MatchProfile
from .protocol import TurnInbox, TurnMessage
from .replay import replay_sequence, verify_audit
from .transport import McpPeerClient, start_server


class PeerPhase(str, Enum):
    STARTING = "starting"
    NEGOTIATING = "negotiating"
    WAITING = "waiting"
    ACTING = "acting"
    AUDITING = "auditing"
    VERIFIED = "verified"
    FAILED = "failed"


UNRESOLVED_GIT_COMMIT = "UNRESOLVED_SELF_TEST_NO_GIT_METADATA"


def require_real_team_git_commit(value: Any, owner: str) -> None:
    """Reject only values forbidden by the explicit real-team provenance gate."""
    if value is None or value == "" or value == UNRESOLVED_GIT_COMMIT:
        raise ValueError(f"real-team Git provenance refused: {owner} commit is unresolved")


@dataclass(slots=True)
class DeadlineTracker:
    timeout: float
    started: float = field(default_factory=time.monotonic)

    def remaining(self) -> float:
        return max(0.0, self.timeout - (time.monotonic() - self.started))


@dataclass(slots=True)
class LocalGameState:
    role: Role
    position: Position
    blocked: frozenset[Position]
    barriers: set[Position] = field(default_factory=set)
    own_moves: int = 0
    own_barriers: int = 0
    own_scent: tuple = ()
    opponent_scent: tuple = ()
    terminal: str | None = None
    pending_claim_response: dict[str, Any] | None = None


def _position(raw: Any) -> Position:
    return Position(int(raw[0]), int(raw[1]))


def config_from_profile(profile: MatchProfile) -> GameConfig:
    cfg = profile.board_config
    return GameConfig(
        board_size=cfg["board_size"],
        police_start=_position(cfg["police_start"]),
        thief_start=_position(cfg["thief_start"]),
        blocked_cells=frozenset(_position(p) for p in cfg.get("blocked_cells", [])),
        barrier_quota=cfg.get("barrier_quota", 14),
        survival_threshold=profile.survival_limit,
        barrier_placement_mode=BarrierPlacementMode(profile.barrier_placement_profile.lower()),
        scent_profile=profile.scent_profile,
    )


def action_to_wire(action: Action | None) -> dict[str, Any] | None:
    if action is None:
        return None
    return {
        "type": action.move_type.value,
        "direction": action.direction.value if action.direction else None,
        "barrier": (
            [action.barrier_position.row, action.barrier_position.col]
            if action.barrier_position
            else None
        ),
    }


def _audit_result(value: str | None) -> str | None:
    if value in {"police_capture", "barrier_on_thief", "thief_boxed_in"}:
        return "capture"
    return value


class PeerRuntime:
    def __init__(
        self,
        role: Role,
        profile: MatchProfile,
        host: str,
        port: int,
        opponent_url: str,
        artifact_dir: Path,
        seed: int = 1,
        hint: str = "שלום 🙂 localhost",
        advertised_url: str | None = None,
        group_id: str | None = None,
        group_name: str | None = None,
        git_commit: str | None = None,
        real_team: bool = False,
    ) -> None:
        self.role, self.profile, self.config = role, profile, config_from_profile(profile)
        self.host, self.port, self.artifact_dir = host, port, artifact_dir
        advertised_url = advertised_url or f"http://{host}:{port}/mcp"
        self.advertised_url = advertised_url
        self.opponent_url = redact_url(opponent_url)
        self.real_team = real_team
        self.git_commit = git_commit if git_commit is not None else UNRESOLVED_GIT_COMMIT
        role_name = "cop" if role is Role.POLICE else "thief"
        self.identity = {
            "group_id": group_id or f"local-{role.value}",
            "group_name": group_name or f"Local {role.value.title()}",
            "members": [],
            "repos": {"cop": "local-unpublished", "thief": "local-unpublished"},
            "mcp_servers": {role_name: advertised_url},
            "llm_model": "deterministic-python",
            "spec": {},
            "github_commit": self.git_commit,
        }
        self.started_at = datetime.now(UTC)
        self.hint = hint
        self.state = LocalGameState(
            role,
            self.config.police_start if role is Role.POLICE else self.config.thief_start,
            self.config.blocked_cells,
        )
        self.backend = ScentTacticalPolice(seed) if role is Role.POLICE else RandomLegalThief(seed)
        self.inboxes = None
        self.client = McpPeerClient(
            opponent_url,
            profile.timeouts["connect"],
            profile.timeouts["retry"],
            int(profile.timeouts.get("retry_count", 100)),
        )
        self.receiver = TurnInbox()
        self._next_outbound_step = 1
        self.phase = PeerPhase.STARTING
        self.peer_identity: dict[str, Any] = {}
        self.records: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []
        self.strategy_ms: list[float] = []
        self.roundtrip_ms: list[float] = []
        self.turn_ms: list[float] = []

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

    def run(self) -> dict[str, Any]:
        try:
            if self.real_team:
                require_real_team_git_commit(self.git_commit, "local")
            self.inboxes = start_server(self.role.value, self.host, self.port)
            self._negotiate()
            if self.role is Role.THIEF:
                self._act_and_send(self._next_outbound())
            while self.state.terminal is None:
                self._receive_and_maybe_act()
            return self._audit_and_finish()
        except Exception as exc:
            self.phase = PeerPhase.FAILED
            return {
                "ok": False,
                "role": self.role.value,
                "phase": self.phase.value,
                "error": f"{type(exc).__name__}: {exc}",
                "events": self.events,
            }

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

    def _next_outbound(self) -> int:
        if self.profile.step_numbering == "sender_local":
            step = self._next_outbound_step
            self._next_outbound_step += 1
            return step
        return self.receiver.next_step

    def _legal_actions(self) -> tuple[Action, ...]:
        occupied = self.state.blocked | frozenset(self.state.barriers)
        actions = []
        for direction in (Direction.N, Direction.S, Direction.E, Direction.W):
            dr, dc = DELTAS[direction]
            target = Position(self.state.position.row + dr, self.state.position.col + dc)
            if (
                0 <= target.row < self.config.board_size
                and 0 <= target.col < self.config.board_size
                and target not in occupied
            ):
                actions.append(Action.move(direction))
        actions.append(Action.stay())
        if self.role is Role.POLICE and self.state.own_barriers < self.config.barrier_quota:
            for direction in (Direction.N, Direction.S, Direction.E, Direction.W):
                dr, dc = DELTAS[direction]
                target = Position(self.state.position.row + dr, self.state.position.col + dc)
                if (
                    0 <= target.row < self.config.board_size
                    and 0 <= target.col < self.config.board_size
                    and target not in occupied
                ):
                    actions.append(Action.barrier(target))
        return tuple(actions)

    def _boxed_in(self) -> bool:
        occupied = self.state.blocked | frozenset(self.state.barriers)
        for direction in (Direction.N, Direction.S, Direction.E, Direction.W):
            dr, dc = DELTAS[direction]
            target = Position(self.state.position.row + dr, self.state.position.col + dc)
            if (
                0 <= target.row < self.config.board_size
                and 0 <= target.col < self.config.board_size
                and target not in occupied
            ):
                return False
        return True

    def _observation(self) -> Observation:
        return Observation(
            RoleLocalState(
                self.role, self.state.position, self.state.own_moves, self.state.own_barriers
            ),
            self.config.board_size,
            self.config.barrier_quota,
            self.state.blocked,
            frozenset(Barrier(p) for p in self.state.barriers),
            self.state.opponent_scent,
            self._legal_actions(),
            None,
        )

    def _act_and_send(self, step: int) -> None:
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
                self.state.position.row + dr, self.state.position.col + dc
            )
        elif action.move_type is MoveType.BARRIER:
            barrier = action.barrier_position
            self.state.barriers.add(barrier)
            self.state.own_barriers += 1
        self.state.own_moves += 1
        self.state.own_scent = scent_model_for(self.profile.scent_profile).advance(
            self.state.own_scent, self.state.position, self.config.board_size
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

    def _send_terminal_response(self, step: int) -> None:
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

    def _audit_and_finish(self) -> dict[str, Any]:
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
        local_check, remote_check = verify_audit(self.records), verify_audit(remote["records"])
        claims_match = _audit_result(remote["result_claim"]) == _audit_result(self.state.terminal)
        verified = local_check["verified"] and remote_check["verified"] and claims_match
        audit_ms = (time.perf_counter() - audit_started) * 1000
        self.phase = PeerPhase.VERIFIED if verified else PeerPhase.FAILED
        peer_group = self.peer_identity.get("group_id", "unknown-peer")
        game_id, game_uid = derive_game_ids(
            self.profile.reference_terms(), self.identity["group_id"], peer_group
        )
        outcome = {
            "game_id": game_id,
            "outcome": _audit_result(self.state.terminal),
            "verified": verified,
            "profile": self.profile.artifact_profile,
        }
        outcome["mutual_agreement"] = consensus_sha256(outcome.copy())
        remote_records = [
            dict(record, _audit_sender=remote["sender"]) for record in remote["records"]
        ]
        combined = sorted(self.records + remote_records, key=lambda r: r["payload"]["step"])
        replay_started = time.perf_counter()
        replay_check = replay_sequence(combined, self.profile.board_config)
        replay_ms = (time.perf_counter() - replay_started) * 1000
        if self.profile.artifact_profile == "reference-v3-artifact-1.1":
            winner = "thief" if _audit_result(self.state.terminal) == "survival" else "police"
            winner_group = (self.identity["group_id"] if self.role.value == winner
                            else peer_group)
            role_groups = {self.identity["group_id"]: self.role.value,
                           peer_group: "thief" if self.role is Role.POLICE else "police"}
            score = score_sub_game(_audit_result(self.state.terminal), role_groups)
            aggregate = aggregate_scores(score)
            ended_at = datetime.now(UTC)
            sub_game = {
                "sub_game_number": 1,
                "roles": role_groups,
                "started_at": self.started_at.isoformat(),
                "ended_at": ended_at.isoformat(),
                "result": _audit_result(self.state.terminal),
                "winner_group": winner_group,
                "github_commit": {
                    self.identity["group_id"]: self.git_commit,
                    peer_group: self.peer_identity.get(
                        "github_commit", UNRESOLVED_GIT_COMMIT
                    ),
                },
                "tokens": dict.fromkeys(role_groups, 0),
                "score": score,
                "log_files": {
                    group: f"{group}/log_{game_id}_g01.json" for group in role_groups
                },
                "audit": {"log_verified": verified, "tampered": not verified},
            }
            mutual_sha = consensus_sha256(
                final_consensus_scope(game_id, aggregate, [sub_game])
            )
            log_summary = {
                "records": combined, "sub_game_number": 1, "role": self.role.value,
                "result": _audit_result(self.state.terminal), "winner": winner,
                "steps": len(combined), "started_at": self.started_at.isoformat(),
                "duration_seconds": (ended_at - self.started_at).total_seconds(),
                "tokens_total": 0,
                "audit": {"passed": verified, "verified_steps": len(combined),
                          "failed_steps": [] if verified else ["audit_or_claim"]},
            }
            paths = write_reference_v3_artifacts(
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
            "artifacts": [str(p) for p in paths],
            "metrics": {
                "strategy_ms": self.strategy_ms,
                "mcp_roundtrip_ms": self.roundtrip_ms,
                "turn_ms": self.turn_ms,
                "audit_ms": audit_ms,
                "replay_ms": replay_ms,
            },
            "events": self.events,
        }


def run_peer(
    role: str,
    profile_path: Path,
    host: str,
    port: int,
    advertised_url: str,
    opponent_url: str,
    artifact_dir: Path,
    output_path: Path,
    seed: int = 1,
    group_id: str | None = None,
    group_name: str | None = None,
    git_commit: str | None = None,
    real_team: bool = False,
) -> int:
    raw = json.loads(profile_path.read_text(encoding="utf-8"))
    profile = MatchProfile(**raw)
    result = PeerRuntime(
        Role(role), profile, host, port, opponent_url, artifact_dir, seed,
        advertised_url=advertised_url, group_id=group_id, group_name=group_name,
        git_commit=git_commit, real_team=real_team,
    ).run()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if result["ok"] else 1
