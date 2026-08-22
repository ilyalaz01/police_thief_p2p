"""Assemble our counted-series bundle from the six public sub-game results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .sdk import PoliceThiefSDK


def build_parser() -> argparse.ArgumentParser:
    """Build the documented series-assembly parser without any side effect."""
    parser = argparse.ArgumentParser(
        description="This command assembles one team's counted six-sub-game bundle.",
        epilog=(
            "It reads only local files, contacts nothing, and mails nothing. Every sub-game "
            "must already be a verified peer result from the agreed public series."
        ),
    )
    parser.add_argument("--our-declaration", type=Path, required=True, help="our declaration JSON")
    parser.add_argument(
        "--peer-declaration", type=Path, required=True, help="the opponent's declaration JSON"
    )
    parser.add_argument(
        "--appendix-b", type=Path, required=True, help="the agreed byte-identical config/game.json"
    )
    parser.add_argument(
        "--result", type=Path, action="append", required=True,
        help="one peer result JSON per sub-game, repeated six times in playing order",
    )
    parser.add_argument("--out", type=Path, required=True, help="output bundle directory")
    parser.add_argument(
        "--max-tokens-per-game", type=int, default=0, help="agreed per-game token cap"
    )
    parser.add_argument(
        "--profile", type=Path, required=True, help="the agreed match profile JSON"
    )
    return parser


def main() -> int:
    """Validate six sub-games, aggregate them, and write this team's bundle."""
    args = build_parser().parse_args()
    if len(args.result) != 6:
        raise SystemExit("a counted series is exactly six sub-games; pass --result six times")
    sdk = PoliceThiefSDK()
    summary = sdk.league.assemble_public_series(
        our_declaration=args.our_declaration,
        peer_declaration=args.peer_declaration,
        appendix_b=args.appendix_b,
        profile=args.profile,
        results=tuple(args.result),
        out=args.out,
        max_tokens_per_game=args.max_tokens_per_game,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
