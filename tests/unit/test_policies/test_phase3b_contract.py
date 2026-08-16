"""Characterization of Phase 3B policy behavior before structural refactoring."""

import hashlib
import inspect
import json
import re

import pytest

from police_thief_lab import Action, Direction, GameConfig, Role, Simulator, policies
from police_thief_lab.policies import (
    BeliefUsage,
    DeterministicSearchPolice,
    OpponentModel,
    TacticalOneStepPolice,
)
from police_thief_lab.policies.phase3b import (
    FEATURES,
    _hypothetical_police_actions,
    modeled_replies,
)


def _action_row(action: Action) -> list[object]:
    barrier = action.barrier_position
    return [
        action.move_type.value,
        action.direction.value if action.direction else None,
        [barrier.row, barrier.col] if barrier else None,
    ]


def _first_police_observation():
    simulator = Simulator(GameConfig())
    simulator.apply(Action.move(Direction.N))
    return simulator.observe(Role.POLICE)


def _search_contract() -> bytes:
    observation = _first_police_observation()
    rows = []
    for model in OpponentModel:
        for usage in BeliefUsage:
            for depth in (1, 2, 3):
                policy = DeterministicSearchPolice(
                    17,
                    opponent_model=model,
                    belief_usage=usage,
                    depth=depth,
                    node_budget=64,
                )
                choice = policy.choose_action(observation)
                rows.append(
                    {
                        "model": model.value,
                        "usage": usage.value,
                        "depth": depth,
                        "choice": _action_row(choice),
                        "nodes": policy.last_search_nodes,
                        "diagnostics": [
                            {
                                "action": _action_row(row.action),
                                "score": round(row.score, 12),
                                "components": {
                                    name: round(value, 12)
                                    for name, value in row.components.items()
                                },
                                "replies": [
                                    [cell.row, cell.col] for cell in row.modeled_replies
                                ],
                            }
                            for row in policy.last_diagnostics
                        ],
                    }
                )
    tactical = TacticalOneStepPolice(4)
    tactical_choice = tactical.choose_action(observation)
    contract = {
        "features": FEATURES,
        "signatures": {
            "search_init": str(inspect.signature(DeterministicSearchPolice)),
            "search_choose": str(inspect.signature(DeterministicSearchPolice.choose_action)),
            "tactical_init": str(inspect.signature(TacticalOneStepPolice)),
            "modeled_replies": str(inspect.signature(modeled_replies)),
            "hypothetical": str(inspect.signature(_hypothetical_police_actions)),
        },
        "rows": rows,
        "tactical": {
            "choice": _action_row(tactical_choice),
            "nodes": tactical.last_search_nodes,
            "scores": [round(row.score, 12) for row in tactical.last_diagnostics],
        },
    }
    return json.dumps(
        contract,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()


def test_phase3b_public_contract_and_seeded_vectors_are_exact() -> None:
    assert policies.DeterministicSearchPolice is DeterministicSearchPolice
    assert policies.TacticalOneStepPolice is TacticalOneStepPolice
    assert len(_search_contract()) == 48145
    assert hashlib.sha256(_search_contract()).hexdigest() == (
        "6966c3d4694911039181bed20568832ee6f1228a636a3f5b7d141fb48bb70457"
    )


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (
            lambda: DeterministicSearchPolice(1, depth=0),
            "depth must be 1..3 and node_budget must be positive",
        ),
        (
            lambda: DeterministicSearchPolice(1, node_budget=0),
            "depth must be 1..3 and node_budget must be positive",
        ),
        (
            lambda: DeterministicSearchPolice(1, disabled_features=frozenset({"unknown"})),
            "unknown disabled features: ['unknown']",
        ),
    ],
)
def test_phase3b_constructor_errors_are_exact(factory, message: str) -> None:
    with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
        factory()
