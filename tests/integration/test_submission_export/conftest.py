"""Shared fixtures for submission_export integration tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _head_commit(repo_root: Path) -> str:
    result = subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={repo_root.as_posix()}",
            "-C",
            str(repo_root),
            "rev-parse",
            "HEAD",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout.strip()


@pytest.fixture
def head_commit(repo_root: Path) -> str:
    """Current HEAD commit SHA from the local repository."""
    return _head_commit(repo_root)


@pytest.fixture
def valid_include() -> list[str]:
    """Minimal tracked include set satisfying Rule 50."""
    return [
        "README.md",
        "config/operational.self-test.v1.json",
        "docs/PLAN.md",
        "docs/PRD.md",
        "docs/TODO.md",
    ]


@pytest.fixture
def police_manifest(head_commit: str, valid_include: list[str]) -> dict:
    """Minimal valid police manifest dict."""
    return {
        "schema": "submission_export_v1",
        "role": "police",
        "source_commit": head_commit,
        "include": list(valid_include),
        "required_paths": ["README.md", "docs/PRD.md", "docs/PLAN.md", "docs/TODO.md"],
        "counterpart_repository_url": "PENDING_HUMAN_APPROVAL",
    }


@pytest.fixture
def thief_manifest(head_commit: str, valid_include: list[str]) -> dict:
    """Minimal valid thief manifest dict."""
    return {
        "schema": "submission_export_v1",
        "role": "thief",
        "source_commit": head_commit,
        "include": list(valid_include),
        "required_paths": ["README.md", "docs/PRD.md", "docs/PLAN.md", "docs/TODO.md"],
        "counterpart_repository_url": "PENDING_HUMAN_APPROVAL",
    }
