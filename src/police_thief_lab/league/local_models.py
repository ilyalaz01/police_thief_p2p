"""Typed inputs and outputs for the uncounted localhost series adapter."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..interop.profile import MatchProfile
from .config import AppendixBConfigLock
from .identity import TeamDeclarationIdentity
from .series import SeriesSlot

UNCOUNTED_LOCALHOST_SELF_TEST = "UNCOUNTED_LOCALHOST_SELF_TEST"


@dataclass(frozen=True, slots=True)
class LocalhostSeriesRequest:
    """Input: sealed local-only plan; output setup: one new artifact directory."""

    profile: MatchProfile
    config_lock: AppendixBConfigLock
    schedule: tuple[SeriesSlot, ...]
    identities: tuple[TeamDeclarationIdentity, TeamDeclarationIdentity]
    commits: Mapping[int, Mapping[str, str]]
    output_dir: Path
    max_tokens_per_game: int
    seed: int = 1
    classification: str = UNCOUNTED_LOCALHOST_SELF_TEST


@dataclass(frozen=True, slots=True)
class LocalhostSeriesResult:
    """Sanitized summary plus paths to the locally generated official artifacts."""

    game_id: str
    game_uid: str
    rows: tuple[dict[str, Any], ...]
    aggregate: dict[str, Any]
    mutual_sha256: str
    peer_checks: tuple[dict[str, Any], ...]
    artifacts: tuple[Path, ...]
    evidence_path: Path
