"""Command-line entry point for the deterministic local sensitivity publication."""

from __future__ import annotations

import argparse
from pathlib import Path

from .publication import build_publication


def parser() -> argparse.ArgumentParser:
    """Build the bounded research-publication argument parser."""
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument(
        "--design", type=Path, default=Path("data/research/sensitivity_design.v1.json")
    )
    value.add_argument("--output-root", type=Path, default=Path("."))
    return value


def main() -> int:
    """Generate the preregistered local publication and return success."""
    args = parser().parse_args()
    manifest = build_publication(args.design, args.output_root)
    print(
        f"generated {len(manifest['artifacts'])} artifacts from "
        f"{manifest['record_count']} local simulator games"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
