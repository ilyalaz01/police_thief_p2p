"""CLI for one history-preserving role repository gate."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from tools.submission_assembly.repository import verify_role_repository

_ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    """Verify one local candidate repository and print sanitized JSON."""
    parser = argparse.ArgumentParser(description="Verify one offline role repository candidate.")
    parser.add_argument("--role", choices=("police", "thief"), required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-root", type=Path, default=_ROOT)
    parser.add_argument(
        "--policy",
        type=Path,
        default=_ROOT / "data/submission/role_content_policy.v1.json",
    )
    args = parser.parse_args(argv)
    try:
        report = verify_role_repository(
            args.source_root,
            args.candidate,
            args.policy,
            args.role,
            args.source_commit,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"ERROR [{type(exc).__name__}]: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
