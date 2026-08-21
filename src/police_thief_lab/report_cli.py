"""CLI for the official counted-series result mail; sending stays a separate decision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .sdk import PoliceThiefSDK


def build_parser() -> argparse.ArgumentParser:
    """Build the documented reporting parser without any side effect."""
    parser = argparse.ArgumentParser(
        description="This command builds the one official result e-mail for a counted game.",
        epilog=(
            "Safety: this command never sends. It has no credential, performs no OAuth, and "
            "contacts no service. An authorized send is a separate, explicitly approved "
            "operation and is not available from this entry point."
        ),
    )
    parser.add_argument("--result", type=Path, required=True, help="mutually agreed result JSON")
    parser.add_argument(
        "--reporting-config", type=Path, required=True, help="operator reporting boundary JSON"
    )
    parser.add_argument("--out", type=Path, help="optional path for the inspectable raw message")
    return parser


def main() -> int:
    """Build one message, report what it contains, and write it only on request."""
    args = build_parser().parse_args()
    sdk = PoliceThiefSDK().reporting
    config = sdk.load_reporting_config(args.reporting_config)
    message = sdk.build_result_message(args.result.read_bytes(), config)
    summary = sdk.GmailResultSender(config).dry_run(message)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(message.raw, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
