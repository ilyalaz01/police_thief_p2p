"""Cross-platform offline-ops CLI entry point.

Dispatches the ``quality-gate``, ``validate-match``, ``package-match``, and
``scan-secrets`` subcommands defined in
``docs/RELEASE_ENGINEERING_WORKSTREAM.md``. Built on ``argparse``,
``pathlib``, and ``subprocess`` argument arrays only: it never constructs
shell command strings and never performs network I/O.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from tools.offline_ops.commands import package_match, quality_gate, scan_secrets, validate_match
from tools.offline_ops.exit_codes import ExitCode
from tools.offline_ops.models import GateReport
from tools.offline_ops.reporting import render_report


def build_parser() -> argparse.ArgumentParser:
    """Build the offline-ops argument parser and its four subcommands."""
    parser = argparse.ArgumentParser(
        prog="offline-ops",
        description="Reproducible local verification and release packaging.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    quality = subparsers.add_parser("quality-gate", help="Run the composed local quality gate.")
    quality.add_argument("--match-path", type=Path, default=None)
    quality.add_argument("--timeout", type=float, default=600.0)

    validate = subparsers.add_parser(
        "validate-match", help="Validate one schema 1.1 match artifact directory."
    )
    validate.add_argument("path", type=Path)

    package = subparsers.add_parser(
        "package-match", help="Validate and package one match artifact directory."
    )
    package.add_argument("path", type=Path)
    package.add_argument("--output", type=Path, required=True)

    scan = subparsers.add_parser("scan-secrets", help="Scan a path for leaked secrets.")
    scan.add_argument("path", type=Path)

    return parser


def _dispatch(args: argparse.Namespace) -> GateReport:
    """Route parsed arguments to the matching command module's ``run``."""
    if args.command == "quality-gate":
        return quality_gate.run(match_path=args.match_path, timeout_seconds=args.timeout)
    if args.command == "validate-match":
        return validate_match.run(args.path)
    if args.command == "package-match":
        return package_match.run(args.path, args.output)
    if args.command == "scan-secrets":
        return scan_secrets.run(args.path)
    raise AssertionError(f"unreachable command: {args.command!r}")


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, dispatch to a subcommand, render, and return its exit code."""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        return code if isinstance(code, int) else int(ExitCode.INVALID_INVOCATION)

    report = _dispatch(args)
    render_report(report)
    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
