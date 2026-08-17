"""Evaluation-only transformations of legally produced scent observations."""

from __future__ import annotations

import random
from dataclasses import replace
from enum import Enum

from ..models import Observation
from ..simulator import DecisionBackend


class ScentAblation(str, Enum):
    """Controlled observation variants that leave game physics untouched."""

    NORMAL = "normal"
    NO_SCENT = "no_scent"
    SHUFFLED_SCENT = "shuffled_scent"
    STALE_SCENT = "stale_scent"


class AblatedBackend:
    """Transform only opponent_scent before delegating to a policy."""

    def __init__(self, backend: DecisionBackend, mode: ScentAblation, seed: int) -> None:
        """Initialize AblatedBackend with its validated setup values and private state."""
        self.backend = backend
        self.mode = mode
        self._random = random.Random(seed)
        self._previous = ()

    def choose_action(self, observation: Observation):
        """Delegate with normal, removed, permuted, or one-observation-old scent."""
        current = observation.opponent_scent
        if self.mode is ScentAblation.NO_SCENT:
            scent = ()
        elif self.mode is ScentAblation.SHUFFLED_SCENT:
            positions = [position for position, _ in current]
            self._random.shuffle(positions)
            scent = tuple(sorted(zip(positions, (value for _, value in current), strict=True)))
        elif self.mode is ScentAblation.STALE_SCENT:
            scent = self._previous
        else:
            scent = current
        self._previous = current
        return self.backend.choose_action(replace(observation, opponent_scent=scent))


class LaggedScentBackend:
    """Supply scent from exactly N prior observations for controlled diagnostics."""

    def __init__(self, backend: DecisionBackend, age: int) -> None:
        """Initialize LaggedScentBackend with its validated setup values and private state."""
        if age < 0:
            raise ValueError("scent age cannot be negative")
        self.backend = backend
        self.age = age
        self._history = []

    def choose_action(self, observation: Observation):
        """Replace only scent; missing early history is represented by an empty field."""
        current = observation.opponent_scent
        self._history.append(current)
        scent = self._history[-self.age - 1] if len(self._history) > self.age else ()
        return self.backend.choose_action(replace(observation, opponent_scent=scent))
