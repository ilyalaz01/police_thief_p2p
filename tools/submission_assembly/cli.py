"""Command-line entry point for offline two-role candidate assembly."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.submission_assembly.assembly import prepare_candidates

_ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    """Prepare both candidates or return a deterministic refusal code."""
    parser = argparse.ArgumentParser(description="Prepare offline Police and Thief candidates.")
    parser.add_argument("output", type=Path, help="New output root for both candidate trees.")
    parser.add_argument(
        "--policy",
        type=Path,
        default=_ROOT / "data/submission/role_content_policy.v1.json",
    )
    parser.add_argument("--repo-root", type=Path, default=_ROOT)
    try:
        args = parser.parse_args(argv)
        prepare_candidates(args.policy, args.output, args.repo_root)
    except (OSError, ValueError) as exc:
        print(f"ERROR [{type(exc).__name__}]: {exc}", file=sys.stderr)
        return 1
    print("Prepared two offline candidate trees; external operations remain blocked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
