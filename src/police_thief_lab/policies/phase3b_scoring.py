"""Private scoring methods extracted unchanged from Phase 3B search."""

from ..models import MoveType, Position
from .geometry import blocked, manhattan, neighbours, reachable_area, target_of
from .phase3b_models import FEATURES
from .phase3b_replies import _hypothetical_police_actions, modeled_replies


class _SearchScoringMixin:
    def _value(self, observation, action, thief: Position):
        if self.last_search_nodes >= self.node_budget:
            return -1000.0, dict.fromkeys(FEATURES, 0.0), ()
        obstacles = blocked(observation)
        police = target_of(action, observation.local.own_position)
        barrier = action.barrier_position if action.move_type is MoveType.BARRIER else None
        after = obstacles | ({barrier} if barrier is not None else set())
        # Phase 3A's critical bug was checking capture only after a reply.
        if police == thief or barrier == thief:
            components = dict.fromkeys(FEATURES, 0.0)
            components["capture_probability"] = 100.0
            return self._sum(components), components, ()
        leaf_scent = self._scent_model.advance(self._own_scent, police, observation.board_size)
        replies = (
            ()
            if self.depth == 1
            else modeled_replies(
                self.opponent_model,
                thief,
                police,
                observation.board_size,
                frozenset(after),
                leaf_scent,
            )
        )
        candidates = replies or (thief,)
        evaluated = []
        for reply in candidates:
            if self.last_search_nodes >= self.node_budget:
                break
            self.last_search_nodes += 1
            components = self._components(observation, police, thief, reply, barrier, after)
            value = self._sum(components)
            if self.depth == 3:
                next_values = [
                    self._simple_next_police_value(observation, candidate, reply, after)
                    for candidate in _hypothetical_police_actions(
                        police,
                        observation.board_size,
                        frozenset(after),
                        observation.local.own_barriers_placed + int(barrier is not None),
                        observation.barrier_quota,
                    )
                ]
                value = max(next_values)
            evaluated.append((value, components))
        if not evaluated:
            components = dict.fromkeys(FEATURES, 0.0)
            return -1000.0, components, replies
        value, components = min(evaluated, key=lambda item: item[0])
        return value, components, replies

    def _components(self, observation, police, old_thief, thief, barrier, obstacles):
        old_area = reachable_area(old_thief, observation.board_size, blocked(observation))
        thief_area = reachable_area(thief, observation.board_size, frozenset(obstacles))
        thief_exits = len(neighbours(thief, observation.board_size, frozenset(obstacles)))
        police_area = reachable_area(police, observation.board_size, frozenset(obstacles))
        police_exits = len(neighbours(police, observation.board_size, frozenset(obstacles)))
        separated = police_area != thief_area
        horizon = max(0, 35 - observation.local.own_moves)
        return {
            "distance_pursuit": -3.0 * manhattan(police, thief),
            "capture_probability": 100.0 * (police == thief),
            "reachable_area_reduction": 0.12 * (old_area - thief_area),
            "opponent_mobility": -0.7 * thief_exits,
            "police_mobility": 0.35 * police_exits,
            "barrier_cost": -1.2 * (barrier is not None),
            "bottleneck_separator": 0.5 * (4 - thief_exits),
            "self_isolation_risk": -6.0 * separated,
            "survival_horizon_urgency": -0.2 * (35 - horizon) / 35,
        }

    def _simple_next_police_value(self, observation, action, thief, obstacles):
        police = target_of(action, observation.local.own_position)
        barrier = action.barrier_position if action.move_type is MoveType.BARRIER else None
        if police == thief or barrier == thief:
            return 100.0 if "capture_probability" not in self.disabled_features else 0.0
        after = obstacles | ({barrier} if barrier is not None else set())
        return self._sum(self._components(observation, police, thief, thief, barrier, after))

    def _sum(self, components: dict[str, float]) -> float:
        return sum(
            value for name, value in components.items() if name not in self.disabled_features
        )
