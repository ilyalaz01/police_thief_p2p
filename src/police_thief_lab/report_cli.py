"""CLI for the official counted-series result mail; sending is an explicit choice."""

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
            "Safety: without --send nothing leaves this machine and no credential is read. "
            "--send performs the authorized league report and must only be used for a counted "
            "game whose result both teams already agreed."
        ),
    )
    parser.add_argument("--result", type=Path, required=True, help="mutually agreed result JSON")
    parser.add_argument(
        "--reporting-config", type=Path, required=True, help="operator reporting boundary JSON"
    )
    parser.add_argument("--out", type=Path, help="optional path for the inspectable raw message")
    parser.add_argument(
        "--send", action="store_true", help="perform the authorized send; requires --credentials"
    )
    parser.add_argument("--credentials", type=Path, help="send-only Gmail credential file")
    parser.add_argument("--audit", type=Path, help="optional path for the retained send record")
    return parser


def main() -> int:
    """Build one message, then either report it or send it exactly once."""
    args = build_parser().parse_args()
    sdk = PoliceThiefSDK().reporting
    config = sdk.load_reporting_config(args.reporting_config)
    message = sdk.build_result_message(args.result.read_bytes(), config)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(message.raw, encoding="utf-8")
    if not args.send:
        print(json.dumps(sdk.GmailResultSender(config).dry_run(message), indent=2))
        return 0
    if args.credentials is None:
        raise SystemExit("--send requires --credentials; refusing to guess a credential location")
    credentials = sdk.load_gmail_credentials(args.credentials)
    transport = sdk.GmailApiTransport(credentials)
    record = sdk.GmailResultSender(config, transport=transport).send(message)
    print(json.dumps(record, indent=2))
    if args.audit is not None:
        args.audit.parent.mkdir(parents=True, exist_ok=True)
        args.audit.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
