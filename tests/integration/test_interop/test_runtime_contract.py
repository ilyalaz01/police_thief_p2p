"""Characterization of runtime public and private contracts before module splitting."""

import hashlib
import inspect
import json

import pytest

from police_thief_lab import Action, Direction, Position
from police_thief_lab.interop import runtime
from police_thief_lab.interop.runtime import (
    UNRESOLVED_GIT_COMMIT,
    DeadlineTracker,
    LocalGameState,
    PeerPhase,
    PeerRuntime,
    _audit_result,
    action_to_wire,
    config_from_profile,
    require_real_team_git_commit,
    run_peer,
)
from tests.support.interop_test_support import profile


def _runtime_contract() -> bytes:
    config = config_from_profile(profile())
    method_names = (
        "_diagnostic",
        "run",
        "_negotiate",
        "_receive_and_maybe_act",
        "_apply_inbound",
        "_next_outbound",
        "_legal_actions",
        "_boxed_in",
        "_observation",
        "_act_and_send",
        "_send_terminal_response",
        "_audit_and_finish",
    )
    value = {
        "phases": [(member.name, member.value) for member in PeerPhase],
        "unresolved": UNRESOLVED_GIT_COMMIT,
        "signatures": {
            "DeadlineTracker": str(inspect.signature(DeadlineTracker)),
            "LocalGameState": str(inspect.signature(LocalGameState)),
            "PeerRuntime": str(inspect.signature(PeerRuntime)),
            "run_peer": str(inspect.signature(run_peer)),
            **{
                name: str(inspect.signature(getattr(PeerRuntime, name)))
                for name in method_names
            },
        },
        "config": {
            "board_size": config.board_size,
            "police_start": [config.police_start.row, config.police_start.col],
            "thief_start": [config.thief_start.row, config.thief_start.col],
            "blocked": sorted([cell.row, cell.col] for cell in config.blocked_cells),
            "barrier_quota": config.barrier_quota,
            "survival_threshold": config.survival_threshold,
            "barrier_placement_mode": config.barrier_placement_mode.value,
            "scent_profile": config.scent_profile,
        },
        "actions": [
            action_to_wire(None),
            action_to_wire(Action.stay()),
            action_to_wire(Action.move(Direction.N)),
            action_to_wire(Action.barrier(Position(2, 3))),
        ],
        "audit_results": [
            _audit_result(value)
            for value in (
                None,
                "police_capture",
                "barrier_on_thief",
                "thief_boxed_in",
                "survival",
                "timeout",
            )
        ],
    }
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def test_runtime_symbols_and_behavioral_contract_are_exact() -> None:
    assert runtime.PeerRuntime is PeerRuntime
    assert PeerRuntime.__module__ == "police_thief_lab.interop.runtime"
    payload = _runtime_contract()
    assert len(payload) == 2403
    assert hashlib.sha256(payload).hexdigest() == (
        "1da7d86790a4fef7cbf07c8ccd545b3b1a07969bff9b59d3b654eed240dd562f"
    )


@pytest.mark.parametrize("value", [None, "", UNRESOLVED_GIT_COMMIT])
def test_real_team_commit_rejection_text_is_exact(value: str | None) -> None:
    with pytest.raises(
        ValueError,
        match="^real-team Git provenance refused: peer commit is unresolved$",
    ):
        require_real_team_git_commit(value, "peer")


def test_real_team_commit_remains_an_opaque_value() -> None:
    require_real_team_git_commit(" feature/Build 07 \t", "peer")
