"""CLI entry point for one independent Police-Thief peer process."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from .interop.runtime_policies import thief_policy_names
from .sdk import PeerLaunchRequest, PoliceThiefSDK


def build_parser() -> argparse.ArgumentParser:
    """Build the documented peer parser without starting any runtime side effect."""
    parser = argparse.ArgumentParser(
        description="This command starts one independent peer process.",
        epilog=(
            "Safety: this command does not authorize external operations. Public transport, "
            "opponent contact, Gmail, and counted matches require separate approval."
        ),
    )
    configured_path = os.environ.get("POLICE_THIEF_CONFIG_PATH")
    parser.add_argument(
        "--role",
        choices=("police", "thief"),
        required=True,
        help="local role for this process",
    )
    parser.add_argument(
        "--operational-config",
        type=Path,
        default=Path(configured_path) if configured_path else None,
        help="strict versioned startup classification JSON",
    )
    parser.add_argument("--profile", type=Path, required=True, help="agreed match-profile JSON")
    parser.add_argument("--host", default="127.0.0.1", help="local listener host")
    parser.add_argument("--port", type=int, required=True, help="local listener port")
    parser.add_argument(
        "--advertised-url",
        help="role-appropriate MCP URL advertised during negotiation",
    )
    parser.add_argument("--group-id", help="local group identifier metadata")
    parser.add_argument("--group-name", help="local group display-name metadata")
    parser.add_argument("--git-commit", help="exact opaque local commit identity")
    parser.add_argument(
        "--declaration",
        type=Path,
        help="operator-supplied declaration JSON with members, repositories and hardware",
    )
    parser.add_argument("--hint", help="free-language hint sent with every turn")
    parser.add_argument(
        "--thief-policy",
        choices=thief_policy_names(),
        help="explicit Thief decision policy; the Police policy stays frozen",
    )
    parser.add_argument(
        "--real-team",
        action="store_true",
        help="enable stricter real-team preflight; this is not authorization",
    )
    parser.add_argument("--opponent-url", required=True, help="opponent FastMCP /mcp endpoint")
    parser.add_argument(
        "--public",
        action="store_true",
        help="require public HTTPS endpoint validation",
    )
    parser.add_argument("--artifacts", type=Path, required=True, help="artifact output directory")
    parser.add_argument("--output", type=Path, required=True, help="peer result JSON path")
    parser.add_argument(
        "--live-view",
        type=Path,
        help="optional role-local Live GUI snapshot JSON path",
    )
    parser.add_argument("--seed", type=int, default=1, help="deterministic local seed")
    return parser


def main() -> int:
    """Parse one peer launch request and delegate it once through the SDK."""
    args = build_parser().parse_args()
    request = PeerLaunchRequest(
        role=args.role,
        profile=args.profile,
        host=args.host,
        port=args.port,
        opponent_url=args.opponent_url,
        artifacts=args.artifacts,
        output=args.output,
        advertised_url=args.advertised_url,
        seed=args.seed,
        group_id=args.group_id,
        group_name=args.group_name,
        git_commit=args.git_commit,
        real_team=args.real_team,
        public=args.public,
        operational_config=args.operational_config,
        live_view=args.live_view,
        declaration=args.declaration,
        hint=args.hint,
        thief_policy=args.thief_policy,
    )
    return PoliceThiefSDK().transport.launch_peer(request)


if __name__ == "__main__":
    raise SystemExit(main())
