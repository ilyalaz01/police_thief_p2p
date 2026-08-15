"""Fast deterministic local simulator with a strict observation boundary."""

from __future__ import annotations

from dataclasses import replace
from typing import Protocol

from .models import (
    Action,
    Barrier,
    GameConfig,
    MoveType,
    Observation,
    Role,
    RoleLocalState,
    WorldState,
)
from .rules import legal_actions, step, validate_action
from .scent import ScentModel, scent_model_for
from .turns import ReferenceV3Alternating


class DecisionBackend(Protocol):
    """Replaceable policy boundary; implementations receive Observation only."""

    def choose_action(self, observation: Observation) -> Action:
        """Choose one of `observation.legal_actions`."""
        ...


class Simulator:
    """Own complete truth while exposing only role-legal immutable observations."""

    def __init__(self, config: GameConfig, scent_model: ScentModel | None = None) -> None:
        """Create a fresh deterministic game and validate its declared scent profile."""
        self.config = config
        self.scent_model = scent_model or scent_model_for(config.scent_profile)
        if self.scent_model.name != config.scent_profile:
            raise ValueError("scent model does not match the declared profile")
        self._state = WorldState(
            police_position=config.police_start,
            thief_position=config.thief_start,
            blocked_cells=config.blocked_cells,
            barriers=frozenset(),
            next_role=ReferenceV3Alternating.first_role(),
        )
        self._actions: list[Action] = []

    @property
    def state(self) -> WorldState:
        """Expose immutable truth to the laboratory controller, never to policies."""
        return self._state

    @property
    def action_log(self) -> tuple[Action, ...]:
        """Return an immutable replay sequence."""
        return tuple(self._actions)

    def observe(self, role: Role) -> Observation:
        """Project complete truth into a role-local view with no opponent position."""
        own_position = (
            self._state.police_position if role is Role.POLICE else self._state.thief_position
        )
        own_moves = self._state.police_moves if role is Role.POLICE else self._state.thief_moves
        placed = self._state.police_barriers_placed if role is Role.POLICE else 0
        opponent_scent = (
            self._state.thief_scent if role is Role.POLICE else self._state.police_scent
        )
        return Observation(
            local=RoleLocalState(role, own_position, own_moves, placed),
            board_size=self.config.board_size,
            barrier_quota=self.config.barrier_quota,
            blocked_cells=self._state.blocked_cells,
            barriers=self._state.barriers,
            opponent_scent=opponent_scent,
            legal_actions=legal_actions(role, self._state, self.config),
            terminal_reason=self._state.terminal_reason,
        )

    def apply(self, action: Action) -> WorldState:
        """Apply exactly one legal serial action and return the new immutable truth."""
        actor = self._state.next_role
        validate_action(action, actor, self._state, self.config)
        state = self._apply_physics(action, actor)
        state = self._advance_scent(state, actor)
        self._state = ReferenceV3Alternating.settle_after_action(state, actor, self.config)
        self._actions.append(action)
        return self._state

    def play_turn(self, backend: DecisionBackend) -> WorldState:
        """Invoke a backend through the observation boundary and apply its action."""
        observation = self.observe(self._state.next_role)
        return self.apply(backend.choose_action(observation))

    def _apply_physics(self, action: Action, actor: Role) -> WorldState:
        state = self._state
        if action.move_type is MoveType.MOVE:
            target = step(
                state.police_position if actor is Role.POLICE else state.thief_position,
                action.direction,
            )
            state = replace(
                state,
                police_position=target if actor is Role.POLICE else state.police_position,
                thief_position=target if actor is Role.THIEF else state.thief_position,
            )
        elif action.move_type is MoveType.BARRIER:
            state = replace(
                state,
                barriers=state.barriers | {Barrier(action.barrier_position)},
                police_barriers_placed=state.police_barriers_placed + 1,
            )
        return replace(
            state,
            police_moves=state.police_moves + (actor is Role.POLICE),
            thief_moves=state.thief_moves + (actor is Role.THIEF),
        )

    def _advance_scent(self, state: WorldState, actor: Role) -> WorldState:
        center = state.police_position if actor is Role.POLICE else state.thief_position
        old_field = state.police_scent if actor is Role.POLICE else state.thief_scent
        field = self.scent_model.advance(old_field, center, self.config.board_size)
        return replace(
            state,
            police_scent=field if actor is Role.POLICE else state.police_scent,
            thief_scent=field if actor is Role.THIEF else state.thief_scent,
        )


def replay(config: GameConfig, actions: tuple[Action, ...]) -> WorldState:
    """Replay a deterministic action sequence from a fresh initial state."""
    simulator = Simulator(config)
    for action in actions:
        simulator.apply(action)
    return simulator.state
