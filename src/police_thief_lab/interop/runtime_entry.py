"""File-oriented entry point for one independent peer runtime."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..models import Role
from .profile import MatchProfile
from .runtime_identity import validate_hint


def run_peer(
    role: str,
    profile_path: Path,
    host: str,
    port: int,
    advertised_url: str,
    opponent_url: str,
    artifact_dir: Path,
    output_path: Path,
    seed: int = 1,
    group_id: str | None = None,
    group_name: str | None = None,
    git_commit: str | None = None,
    real_team: bool = False,
    live_view_path: Path | None = None,
    declaration: dict[str, Any] | None = None,
    hint: str | None = None,
    thief_policy: str | None = None,
) -> int:
    """Load one profile, run one peer, and retain its result JSON."""
    from .runtime import PeerRuntime

    raw = json.loads(profile_path.read_text(encoding="utf-8"))
    profile = MatchProfile(**raw)
    optional: dict[str, Any] = {}
    if hint is not None:
        optional["hint"] = validate_hint(hint, profile.reference_terms()["hint_max_words"])
    result = PeerRuntime(
        Role(role),
        profile,
        host,
        port,
        opponent_url,
        artifact_dir,
        seed,
        advertised_url=advertised_url,
        group_id=group_id,
        group_name=group_name,
        git_commit=git_commit,
        real_team=real_team,
        live_view_path=live_view_path,
        declaration=declaration,
        thief_policy=thief_policy,
        **optional,
    ).run()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return 0 if result["ok"] else 1
