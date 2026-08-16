"""CLI entry point for one independent localhost peer process."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from .sdk import PeerLaunchRequest, PoliceThiefSDK


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=("police", "thief"), required=True)
    configured_path = os.environ.get("POLICE_THIEF_CONFIG_PATH")
    parser.add_argument(
        "--operational-config",
        type=Path,
        default=Path(configured_path) if configured_path else None,
    )
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--advertised-url")
    parser.add_argument("--group-id")
    parser.add_argument("--group-name")
    parser.add_argument("--git-commit")
    parser.add_argument("--real-team", action="store_true")
    parser.add_argument("--opponent-url", required=True)
    parser.add_argument("--public", action="store_true")
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()
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
    )
    return PoliceThiefSDK().transport.launch_peer(request)


if __name__ == "__main__":
    raise SystemExit(main())
