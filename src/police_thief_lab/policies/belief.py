"""History-aware, observation-only belief estimators for Phase 3A."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Protocol

from ..models import Observation, Position
from ..scent import ReferenceSubtractiveChebyshevV1
from .belief_support import _entropy, _field_error, _open_cells
from .geometry import blocked, neighbours


@dataclass(frozen=True, slots=True)
class BeliefDiagnostics:
    """Policy-safe diagnostics; deliberately contains no evaluator truth."""

    updates: int
    hypotheses: int
    entropy: float
    last_update_seconds: float


class BeliefEstimator(Protocol):
    """Replaceable estimator boundary accepting legal observations only."""

    def update(self, observation: Observation) -> None:
        """Incorporate one legally visible observation."""
        ...

    def distribution(self) -> dict[Position, float]:
        """Return a normalized current-position marginal."""
        ...

    def diagnostics(self) -> BeliefDiagnostics:
        """Return truth-free runtime diagnostics."""
        ...


class CurrentScentBelief:
    """Normalized current scent weighting, matching the Phase 2 approximation."""

    def __init__(self) -> None:
        self._distribution: dict[Position, float] = {}
        self._updates = 0
        self._last_update_seconds = 0.0

    def update(self, observation: Observation) -> None:
        started = time.perf_counter()
        obstacles = blocked(observation)
        positive = {
            cell: value
            for cell, value in observation.opponent_scent
            if value > 0 and cell not in obstacles
        }
        if positive:
            total = sum(positive.values())
            self._distribution = {cell: value / total for cell, value in positive.items()}
        else:
            cells = _open_cells(observation)
            self._distribution = {cell: 1 / len(cells) for cell in cells}
        self._updates += 1
        self._last_update_seconds = time.perf_counter() - started

    def distribution(self) -> dict[Position, float]:
        return dict(self._distribution)

    def diagnostics(self) -> BeliefDiagnostics:
        return BeliefDiagnostics(
            self._updates,
            len(self._distribution),
            _entropy(self._distribution),
            self._last_update_seconds,
        )


@dataclass(frozen=True, slots=True)
class _Trajectory:
    positions: tuple[Position, ...]
    weight: float


class TrajectoryBeamBelief:
    """Bounded trajectory beam approximating path-dependent scent likelihoods.

    This is intentionally not described as an exact 49-cell Bayes filter: each
    hypothesis retains recent positions because the observed scent field depends
    on the opponent's path. Older scent is truncated at configurable ``history_k``.
    """

    def __init__(self, history_k: int = 6, beam_width: int = 128) -> None:
        if history_k < 1 or beam_width < 1:
            raise ValueError("history_k and beam_width must be positive")
        self.history_k = history_k
        self.beam_width = beam_width
        self._beam: tuple[_Trajectory, ...] = ()
        self._distribution: dict[Position, float] = {}
        self._updates = 0
        self._last_update_seconds = 0.0
        self._scent_model = ReferenceSubtractiveChebyshevV1()

    @property
    def trajectories(self) -> tuple[tuple[Position, ...], ...]:
        """Expose immutable hypotheses for tests/debugging, never hidden truth."""
        return tuple(item.positions for item in self._beam)

    def update(self, observation: Observation) -> None:
        started = time.perf_counter()
        obstacles = blocked(observation)
        observed = dict(observation.opponent_scent)
        if not self._beam:
            candidates = (_Trajectory((cell,), 1.0) for cell in _open_cells(observation))
        else:
            candidates = (
                _Trajectory((*item.positions, cell)[-self.history_k :], item.weight)
                for item in self._beam
                for cell in (
                    *neighbours(item.positions[-1], observation.board_size, obstacles),
                    item.positions[-1],
                )
                if cell not in obstacles
            )
        scored = []
        for item in candidates:
            predicted = ()
            for cell in item.positions:
                predicted = self._scent_model.advance(predicted, cell, observation.board_size)
            error = _field_error(dict(predicted), observed, observation.board_size)
            # A soft likelihood preserves diversity under truncated history/model mismatch.
            scored.append(_Trajectory(item.positions, item.weight * math.exp(-2.5 * error)))
        scored.sort(key=lambda item: (-item.weight, item.positions))
        self._beam = tuple(scored[: self.beam_width])
        total = sum(item.weight for item in self._beam)
        if total <= 0:
            uniform = 1 / len(self._beam)
            self._beam = tuple(_Trajectory(item.positions, uniform) for item in self._beam)
        else:
            self._beam = tuple(
                _Trajectory(item.positions, item.weight / total) for item in self._beam
            )
        marginal: dict[Position, float] = {}
        for item in self._beam:
            marginal[item.positions[-1]] = marginal.get(item.positions[-1], 0.0) + item.weight
        self._distribution = marginal
        self._updates += 1
        self._last_update_seconds = time.perf_counter() - started

    def distribution(self) -> dict[Position, float]:
        return dict(self._distribution)

    def diagnostics(self) -> BeliefDiagnostics:
        return BeliefDiagnostics(
            self._updates, len(self._beam), _entropy(self._distribution), self._last_update_seconds
        )


def scent_weights(observation: Observation) -> dict[Position, float]:
    """Backward-compatible normalized current-scent helper."""
    estimator = CurrentScentBelief()
    estimator.update(observation)
    return estimator.distribution()
