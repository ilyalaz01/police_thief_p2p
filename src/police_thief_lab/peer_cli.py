"""CLI entry point for one independent localhost peer process."""

from __future__ import annotations

import argparse
from pathlib import Path

from .interop.network import EndpointConfig
from .interop.runtime import run_peer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=("police", "thief"), required=True)
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
    advertised = args.advertised_url or f"http://{args.host}:{args.port}/mcp"
    # Parse the profile before starting a listener so malformed public settings fail fast.
    import json

    timeouts = json.loads(args.profile.read_text(encoding="utf-8"))["timeouts"]
    EndpointConfig(
        args.host,
        args.port,
        advertised,
        args.opponent_url,
        timeouts["connect"],
        timeouts["turn"],
        timeouts["retry"],
        int(timeouts.get("retry_count", 100)),
        timeouts["audit"],
        args.public,
    )
    return run_peer(
        args.role,
        args.profile,
        args.host,
        args.port,
        advertised,
        args.opponent_url,
        args.artifacts,
        args.output,
        args.seed,
        args.group_id,
        args.group_name,
        args.git_commit,
        args.real_team,
    )


if __name__ == "__main__":
    raise SystemExit(main())
