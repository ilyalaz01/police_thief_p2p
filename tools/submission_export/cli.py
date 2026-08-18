"""CLI entry point for the offline submission export tool.

Provides two subcommands:
  plan    — validate a manifest and print the deterministic export plan.
  export  — copy the validated file set into an empty output directory.

Built on argparse and pathlib only; no network I/O is performed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.submission_export.exporter import export_to
from tools.submission_export.manifest import ManifestError
from tools.submission_export.path_guard import PathViolationError
from tools.submission_export.planner import plan as run_plan

_REPO_ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    """Build the submission-export argument parser with plan and export subcommands."""
    parser = argparse.ArgumentParser(
        prog="submission-export",
        description="Offline deterministic submission export and validation tool.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_REPO_ROOT,
        help="Repository root (default: auto-detected from script location).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    plan_p = sub.add_parser("plan", help="Validate manifest and print export plan JSON.")
    plan_p.add_argument("manifest", type=Path, help="Path to the JSON manifest file.")

    exp_p = sub.add_parser(
        "export", help="Copy validated file set into an empty output directory."
    )
    exp_p.add_argument("manifest", type=Path, help="Path to the JSON manifest file.")
    exp_p.add_argument("output_dir", type=Path, help="Empty destination directory.")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run the requested command, print JSON, and return exit code."""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2

    try:
        if args.command == "plan":
            result = run_plan(args.manifest, args.repo_root)
        else:
            result = export_to(args.manifest, args.output_dir, args.repo_root)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (ManifestError, PathViolationError, ValueError) as exc:
        print(f"ERROR [{type(exc).__name__}]: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"ERROR [FileNotFoundError]: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
