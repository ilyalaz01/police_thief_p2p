"""Local board and observation methods for the peer runtime."""

from __future__ import annotations

from ..models import Action, Barrier, Direction, Observation, Position, Role, RoleLocalState
from ..rules import DELTAS


class _RuntimeBoardMixin:
    """Represent RuntimeBoardMixin as one cohesive typed implementation boundary."""
    def _next_outbound(self) -> int:
        """Compute the internal next outbound step used by _RuntimeBoardMixin."""
        if self.profile.step_numbering == "sender_local":
            step = self._next_outbound_step
            self._next_outbound_step += 1
            return step
        return self.receiver.next_step

    def _legal_actions(self) -> tuple[Action, ...]:
        """Compute the internal legal actions step used by _RuntimeBoardMixin."""
        occupied = self.state.blocked | frozenset(self.state.barriers)
        actions = []
        for direction in (Direction.N, Direction.S, Direction.E, Direction.W):
            dr, dc = DELTAS[direction]
            target = Position(self.state.position.row + dr, self.state.position.col + dc)
            if (
                0 <= target.row < self.config.board_size
                and 0 <= target.col < self.config.board_size
                and target not in occupied
            ):
                actions.append(Action.move(direction))
        actions.append(Action.stay())
        if self.role is Role.POLICE and self.state.own_barriers < self.config.barrier_quota:
            for direction in (Direction.N, Direction.S, Direction.E, Direction.W):
                dr, dc = DELTAS[direction]
                target = Position(self.state.position.row + dr, self.state.position.col + dc)
                if (
                    0 <= target.row < self.config.board_size
                    and 0 <= target.col < self.config.board_size
                    and target not in occupied
                ):
                    actions.append(Action.barrier(target))
        return tuple(actions)

    def _boxed_in(self) -> bool:
        """Compute the internal boxed in step used by _RuntimeBoardMixin."""
        occupied = self.state.blocked | frozenset(self.state.barriers)
        for direction in (Direction.N, Direction.S, Direction.E, Direction.W):
            dr, dc = DELTAS[direction]
            target = Position(self.state.position.row + dr, self.state.position.col + dc)
            if (
                0 <= target.row < self.config.board_size
                and 0 <= target.col < self.config.board_size
                and target not in occupied
            ):
                return False
        return True

    def _observation(self) -> Observation:
        """Compute the internal observation step used by _RuntimeBoardMixin."""
        return Observation(
            RoleLocalState(
                self.role,
                self.state.position,
                self.state.own_moves,
                self.state.own_barriers,
            ),
            self.config.board_size,
            self.config.barrier_quota,
            self.state.blocked,
            frozenset(Barrier(p) for p in self.state.barriers),
            self.state.opponent_scent,
            self._legal_actions(),
            None,
        )
