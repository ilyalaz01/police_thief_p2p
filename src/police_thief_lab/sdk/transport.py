"""Peer startup and transport operations exposed through the SDK."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ..configuration import load_operational_config
from ..gatekeeper import (
    ApiGatekeeper,
    GatekeeperBackpressure,
    QueueStatus,
    RateLimitConfig,
    default_gatekeeper,
    load_rate_limit_config,
)
from ..interop.network import EndpointConfig, redact_secrets, redact_url, validate_mcp_url
from ..interop.profile import MatchProfile
from ..interop.protocol import Equivocation, ProtocolViolation, TurnInbox, TurnMessage
from ..interop.runtime import PeerRuntime
from ..interop.runtime import run_peer as _run_peer
from ..interop.runtime_models import (
    DeadlineTracker,
    LocalGameState,
    PeerPhase,
    action_to_wire,
    config_from_profile,
    require_real_team_git_commit,
)
from ..interop.runtime_policies import (
    DEFAULT_THIEF_POLICY,
    build_thief_backend,
    thief_policy_names,
)
from ..interop.transport import (
    McpPeerClient,
    PeerInboxes,
    build_server,
    discover_tools,
    start_server,
)
from ..league.declaration_input import load_declaration_identity


@dataclass(frozen=True, slots=True)
class PeerLaunchRequest:
    """Typed CLI-to-SDK request; values retain the established runtime meanings."""

    role: str
    profile: Path
    host: str
    port: int
    opponent_url: str
    artifacts: Path
    output: Path
    advertised_url: str | None = None
    seed: int = 1
    group_id: str | None = None
    group_name: str | None = None
    git_commit: str | None = None
    real_team: bool = False
    public: bool = False
    operational_config: Path | None = None
    live_view: Path | None = None
    declaration: Path | None = None
    hint: str | None = None
    thief_policy: str | None = None


def launch_peer(request: PeerLaunchRequest) -> int:
    """Validate startup boundaries, then delegate once to the existing peer runtime."""
    if request.operational_config is not None:
        operational = load_operational_config(request.operational_config)
        requested_mode = "real_team" if request.real_team else "self_test"
        if operational.operation_mode != requested_mode:
            raise ValueError("operational config mode does not match the requested peer operation")
    declaration = (
        load_declaration_identity(request.declaration)
        if request.declaration is not None
        else None
    )
    advertised = request.advertised_url or f"http://{request.host}:{request.port}/mcp"
    timeouts = json.loads(request.profile.read_text(encoding="utf-8"))["timeouts"]
    EndpointConfig(
        request.host,
        request.port,
        advertised,
        request.opponent_url,
        timeouts["connect"],
        timeouts["turn"],
        timeouts["retry"],
        int(timeouts.get("retry_count", 100)),
        timeouts["audit"],
        request.public,
    )
    return _run_peer(
        request.role,
        request.profile,
        request.host,
        request.port,
        advertised,
        request.opponent_url,
        request.artifacts,
        request.output,
        request.seed,
        request.group_id,
        request.group_name,
        request.git_commit,
        request.real_team,
        request.live_view,
        declaration.object() if declaration is not None else None,
        request.hint,
        request.thief_policy,
    )


class TransportSDK:
    """Stable peer, profile, protocol, endpoint, and runtime entry points."""

    DeadlineTracker = DeadlineTracker
    ApiGatekeeper = ApiGatekeeper
    EndpointConfig = EndpointConfig
    Equivocation = Equivocation
    GatekeeperBackpressure = GatekeeperBackpressure
    LocalGameState = LocalGameState
    MatchProfile = MatchProfile
    McpPeerClient = McpPeerClient
    PeerInboxes = PeerInboxes
    PeerLaunchRequest = PeerLaunchRequest
    PeerPhase = PeerPhase
    PeerRuntime = PeerRuntime
    ProtocolViolation = ProtocolViolation
    QueueStatus = QueueStatus
    RateLimitConfig = RateLimitConfig
    TurnInbox = TurnInbox
    TurnMessage = TurnMessage
    DEFAULT_THIEF_POLICY = DEFAULT_THIEF_POLICY
    build_thief_backend = staticmethod(build_thief_backend)
    thief_policy_names = staticmethod(thief_policy_names)
    build_server = staticmethod(build_server)
    action_to_wire = staticmethod(action_to_wire)
    config_from_profile = staticmethod(config_from_profile)
    discover_tools = staticmethod(discover_tools)
    default_gatekeeper = staticmethod(default_gatekeeper)
    launch_peer = staticmethod(launch_peer)
    load_rate_limit_config = staticmethod(load_rate_limit_config)
    redact_secrets = staticmethod(redact_secrets)
    redact_url = staticmethod(redact_url)
    require_real_team_git_commit = staticmethod(require_real_team_git_commit)
    run_peer = staticmethod(_run_peer)
    start_server = staticmethod(start_server)
    validate_mcp_url = staticmethod(validate_mcp_url)
