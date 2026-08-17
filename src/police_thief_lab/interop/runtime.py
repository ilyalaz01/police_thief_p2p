"""Independent-process Phase 4A peer state machine."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..models import Role
from ..policies.baselines import RandomLegalThief
from ..policies.tactical import ScentTacticalPolice
from ..presentation import LiveViewPublisher, TurnBanner
from . import runtime_models as _runtime_models
from .network import redact_url
from .profile import MatchProfile
from .protocol import TurnInbox
from .runtime_artifacts import _RuntimeArtifactsMixin
from .runtime_audit import _RuntimeAuditMixin
from .runtime_board import _RuntimeBoardMixin
from .runtime_entry import run_peer as run_peer
from .runtime_lifecycle import _RuntimeLifecycleMixin
from .runtime_presentation import _RuntimePresentationMixin
from .runtime_sending import _RuntimeSendingMixin
from .transport import McpPeerClient, start_server

UNRESOLVED_GIT_COMMIT = _runtime_models.UNRESOLVED_GIT_COMMIT
DeadlineTracker = _runtime_models.DeadlineTracker
LocalGameState = _runtime_models.LocalGameState
PeerPhase = _runtime_models.PeerPhase
_audit_result = _runtime_models._audit_result
_position = _runtime_models._position
action_to_wire = _runtime_models.action_to_wire
config_from_profile = _runtime_models.config_from_profile
require_real_team_git_commit = _runtime_models.require_real_team_git_commit


class PeerRuntime(
    _RuntimeLifecycleMixin,
    _RuntimeBoardMixin,
    _RuntimeSendingMixin,
    _RuntimeAuditMixin,
    _RuntimeArtifactsMixin,
    _RuntimePresentationMixin,
):
    """Represent PeerRuntime as one cohesive typed implementation boundary."""
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
        live_view_path: Path | None = None,
    ) -> None:
        """Initialize PeerRuntime with its validated setup values and private state."""
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
        self.live_view_publisher = (
            LiveViewPublisher(live_view_path) if live_view_path is not None else None
        )
        self.strategy_ms: list[float] = []
        self.roundtrip_ms: list[float] = []
        self.turn_ms: list[float] = []

    def run(self) -> dict[str, Any]:
        """Execute the bounded lifecycle and return its terminal result."""
        try:
            self._publish_live(TurnBanner.LOCKED)
            if self.real_team:
                require_real_team_git_commit(self.git_commit, "local")
            self.inboxes = start_server(self.role.value, self.host, self.port)
            self._negotiate()
            if self.role is Role.THIEF:
                self._publish_live(TurnBanner.YOUR_TURN)
                self._act_and_send(self._next_outbound())
            while self.state.terminal is None:
                self._receive_and_maybe_act()
            result = self._audit_and_finish()
            self._publish_live(TurnBanner.GAME_OVER if result["ok"] else TurnBanner.ERROR)
            return result
        except Exception as exc:
            self.phase = PeerPhase.FAILED
            self._publish_live_error()
            return {
                "ok": False,
                "role": self.role.value,
                "phase": self.phase.value,
                "error": f"{type(exc).__name__}: {exc}",
                "events": self.events,
            }
