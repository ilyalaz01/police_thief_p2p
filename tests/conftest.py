"""Shared fixtures and automatic layer markers for the project test suite."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.support.interop_test_support import free_port, profile
from tests.support.project_paths import PROJECT_ROOT

if TYPE_CHECKING:
    from police_thief_lab.interop.profile import MatchProfile

TEST_ROOT = PROJECT_ROOT / "tests"
LAYERS = {"unit", "integration", "system", "offline_ops"}


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Return the repository root without depending on test nesting depth."""
    return PROJECT_ROOT


@pytest.fixture
def match_profile() -> MatchProfile:
    """Return the shared deterministic interoperability profile."""
    return profile()


@pytest.fixture
def free_tcp_port() -> int:
    """Reserve a currently free local TCP port for one test."""
    return free_port()


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark tests from their documented top-level layer."""
    for item in items:
        relative = Path(str(item.path)).resolve().relative_to(TEST_ROOT)
        if relative.parts and relative.parts[0] in LAYERS:
            item.add_marker(relative.parts[0])
