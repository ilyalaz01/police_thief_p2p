"""Explicit Thief policy selection and the frozen Police boundary."""

from pathlib import Path

import pytest

from police_thief_lab import Role
from police_thief_lab.interop.runtime import PeerRuntime
from police_thief_lab.interop.runtime_policies import (
    DEFAULT_THIEF_POLICY,
    build_thief_backend,
    thief_policy_names,
)
from police_thief_lab.policies import (
    LookaheadEvasionThief,
    RandomLegalThief,
    ScentTacticalPolice,
)
from tests.support.interop_test_support import free_port, profile


def _runtime(role: Role, tmp_path: Path, **kwargs: object) -> PeerRuntime:
    """Build one offline runtime that never contacts a peer."""
    return PeerRuntime(
        role, profile(), "127.0.0.1", free_port(), "http://127.0.0.1:1/mcp", tmp_path, **kwargs
    )


def test_the_accepted_default_thief_policy_is_the_measured_one(tmp_path: Path) -> None:
    assert DEFAULT_THIEF_POLICY == "LookaheadEvasionThief"
    assert isinstance(_runtime(Role.THIEF, tmp_path).backend, LookaheadEvasionThief)
    assert isinstance(build_thief_backend(None, 1), LookaheadEvasionThief)
    assert isinstance(build_thief_backend("RandomLegalThief", 1), RandomLegalThief)


@pytest.mark.parametrize("name", thief_policy_names())
def test_every_offered_policy_builds_and_reaches_the_runtime(name: str, tmp_path: Path) -> None:
    backend = build_thief_backend(name, 1)
    assert type(backend).__name__ == name
    runtime = _runtime(Role.THIEF, tmp_path, thief_policy=name)
    assert type(runtime.backend).__name__ == name


def test_an_unknown_policy_name_is_refused_rather_than_defaulted() -> None:
    with pytest.raises(ValueError, match="unsupported thief policy"):
        build_thief_backend("NoSuchThief", 1)


def test_the_police_policy_stays_frozen_and_unselectable(tmp_path: Path) -> None:
    assert isinstance(_runtime(Role.POLICE, tmp_path).backend, ScentTacticalPolice)
    with pytest.raises(ValueError, match="frozen Police role"):
        _runtime(Role.POLICE, tmp_path, thief_policy="LookaheadEvasionThief")


def test_selected_policies_stay_observation_only(tmp_path: Path) -> None:
    runtime = _runtime(Role.THIEF, tmp_path, thief_policy="LookaheadEvasionThief")
    observation = runtime._observation()
    assert not hasattr(observation, "opponent_position")
    action = runtime.backend.choose_action(observation)
    assert action in observation.legal_actions
