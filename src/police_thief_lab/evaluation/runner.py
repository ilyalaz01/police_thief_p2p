"""Fast in-memory game and batch execution with evaluator-only truth diagnostics."""

from __future__ import annotations

import statistics
import time
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable

from ..models import GameConfig, Position, Role, TerminalReason
from ..policies.geometry import reachable_area
from ..policies.partition import PartitionPolice
from ..rules import IllegalAction
from ..simulator import DecisionBackend, Simulator
from .models import BatchResult, GameResult

PolicyFactory = Callable[[int], DecisionBackend]


def run_game(
    config: GameConfig,
    seed: int,
    police_factory: PolicyFactory,
    thief_factory: PolicyFactory,
    scenario: str = "default",
) -> GameResult:
    """Run one local game; policies receive observations while diagnostics retain truth."""
    simulator = Simulator(config)
    police = police_factory(seed * 2 + 1)
    thief = thief_factory(seed * 2 + 2)
    obstacles = config.blocked_cells
    initial_area = reachable_area(config.thief_start, config.board_size, obstacles)
    illegal = crossings = wrong_side = completed = 0
    previous_side: bool | None = None
    while simulator.state.terminal_reason is None:
        actor = simulator.state.next_role
        backend = police if actor is Role.POLICE else thief
        before_barriers = simulator.state.police_barriers_placed
        try:
            simulator.play_turn(backend)
        except IllegalAction:
            illegal += 1
            simulator.apply(simulator.observe(actor).legal_actions[0])
        if isinstance(police, PartitionPolice) and police.plan is not None:
            plan = police.plan
            side = _low_side(simulator.state.thief_position, plan.axis, plan.index)
            barrier_cells = {barrier.position for barrier in simulator.state.barriers}
            plan_complete = all(cell in barrier_cells for cell in plan.targets)
            if previous_side is not None and side != previous_side and not plan_complete:
                crossings += 1
            if plan_complete and simulator.state.police_barriers_placed > before_barriers:
                completed += 1
                police_side = _low_side(simulator.state.police_position, plan.axis, plan.index)
                wrong_side += police_side != side
            previous_side = side
    state = simulator.state
    final_obstacles = state.blocked_cells | frozenset(
        barrier.position for barrier in state.barriers
    )
    return GameResult(
        seed=seed,
        scenario=scenario,
        terminal_reason=state.terminal_reason.value,
        police_score=state.score.police,
        thief_score=state.score.thief,
        thief_actions=state.thief_moves,
        police_actions=state.police_moves,
        barriers_placed=state.police_barriers_placed,
        illegal_actions=illegal,
        reachable_area_initial=initial_area,
        reachable_area_final=reachable_area(
            state.thief_position, config.board_size, final_obstacles
        ),
        separator_completed=completed,
        wrong_side_cuts=wrong_side,
        unfinished_crossings=crossings,
        tactical_barriers_attempted=getattr(police, "barriers_attempted", 0),
        tactical_barrier_captures=int(
            hasattr(police, "barriers_attempted")
            and state.terminal_reason is TerminalReason.BARRIER_ON_THIEF
        ),
        tactical_area_reduction=getattr(police, "area_reduction_from_barriers", 0),
        tactical_unproductive_barriers=getattr(police, "unproductive_barriers", 0),
    )


def run_batch(
    configs: Iterable[tuple[str, GameConfig]],
    seeds: Iterable[int],
    police_factory: PolicyFactory,
    thief_factory: PolicyFactory,
    police_name: str,
    thief_name: str,
) -> BatchResult:
    """Run the Cartesian scenario/seed set, suitable for paired comparisons."""
    started = time.perf_counter()
    games = tuple(
        run_game(config, seed, police_factory, thief_factory, scenario)
        for scenario, config in configs
        for seed in seeds
    )
    elapsed = time.perf_counter() - started
    return BatchResult(police_name, thief_name, games, elapsed, _aggregate(games, elapsed))


def _aggregate(games: tuple[GameResult, ...], elapsed: float) -> dict:
    """Compute the internal aggregate step used by module."""
    captures = sum(game.terminal_reason != TerminalReason.THIEF_SURVIVED.value for game in games)
    thief_actions = [game.thief_actions for game in games]
    by_scenario: dict[str, list[GameResult]] = defaultdict(list)
    for game in games:
        by_scenario[game.scenario].append(game)
    seed_rates = defaultdict(list)
    for game in games:
        seed_rates[game.seed].append(game.terminal_reason != TerminalReason.THIEF_SURVIVED.value)
    return {
        "games": len(games),
        "police_score": sum(game.police_score for game in games),
        "thief_score": sum(game.thief_score for game in games),
        "capture_rate": captures / len(games),
        "survival_rate": 1 - captures / len(games),
        "terminal_reasons": dict(sorted(Counter(g.terminal_reason for g in games).items())),
        "mean_thief_actions": statistics.fmean(thief_actions),
        "median_thief_actions": statistics.median(thief_actions),
        "mean_police_actions": statistics.fmean(g.police_actions for g in games),
        "mean_barriers_placed": statistics.fmean(g.barriers_placed for g in games),
        "games_per_second": len(games) / elapsed,
        "illegal_action_count": sum(g.illegal_actions for g in games),
        "capture_rate_variance_across_seeds": statistics.pvariance(
            [statistics.fmean(values) for values in seed_rates.values()]
        ),
        "results_by_starting_configuration": {
            name: {
                "games": len(rows),
                "capture_rate": sum(result.terminal_reason != "thief_survived" for result in rows)
                / len(rows),
            }
            for name, rows in sorted(by_scenario.items())
        },
        "separator_completed": sum(g.separator_completed for g in games),
        "wrong_side_cuts": sum(g.wrong_side_cuts for g in games),
        "unfinished_crossings": sum(g.unfinished_crossings for g in games),
        "mean_reachable_area_reduction": statistics.fmean(
            g.reachable_area_initial - g.reachable_area_final for g in games
        ),
        "tactical_barriers_attempted": sum(g.tactical_barriers_attempted for g in games),
        "tactical_barrier_captures": sum(g.tactical_barrier_captures for g in games),
        "tactical_mean_area_reduction_per_barrier": (
            sum(g.tactical_area_reduction for g in games)
            / max(1, sum(g.tactical_barriers_attempted for g in games))
        ),
        "tactical_unproductive_barriers": sum(g.tactical_unproductive_barriers for g in games),
    }


def _low_side(position: Position, axis: str, index: int) -> bool:
    """Compute the internal low side step used by module."""
    return position.col < index if axis == "vertical" else position.row < index
