"""Run preregistered local games and retain only public-safe result fields."""

from __future__ import annotations

from typing import Any

from .design import SDK, game_config, iter_cases, policy_factories
from .statistics import effects, summarize


def build_payload(design: dict[str, Any]) -> dict[str, Any]:
    """Execute every paired case and return deterministic raw and aggregate evidence."""
    police_factories, thief_factories = policy_factories(design)
    records: list[dict[str, Any]] = []
    for setting, scenario, seed in iter_cases(design):
        config = game_config(setting, scenario)
        for police_name in design["policies"]["police"]:
            for thief_name in design["policies"]["thief"]:
                game = SDK.evaluation.run_game(
                    config,
                    seed,
                    police_factories[police_name],
                    thief_factories[thief_name],
                    scenario["id"],
                )
                records.append(_record(setting, police_name, thief_name, game))
    if len(records) != design["expected_games"]:
        raise RuntimeError("experiment produced an unexpected game count")
    summary = summarize(records)
    return {
        "_schema": "police_thief_sensitivity_results_v1",
        "operation_class": "LOCAL_SIMULATOR_EXPERIMENT",
        "method": design["method"],
        "record_count": len(records),
        "records": records,
        "summary": summary,
        "effects": effects(summary, design),
    }


def _record(setting: dict[str, Any], police: str, thief: str, game) -> dict[str, Any]:
    """Project one evaluator result into the approved public-safe row schema."""
    return {
        "setting": setting["id"],
        "factor": setting["factor"],
        "factor_value": setting["value"],
        "board_size": setting["board_size"],
        "survival_threshold": setting["survival_threshold"],
        "scenario": game.scenario,
        "seed": game.seed,
        "police_policy": police,
        "thief_policy": thief,
        "terminal_reason": game.terminal_reason,
        "captured": game.terminal_reason != "thief_survived",
        "police_score": game.police_score,
        "thief_score": game.thief_score,
        "police_actions": game.police_actions,
        "thief_actions": game.thief_actions,
        "barriers_placed": game.barriers_placed,
        "illegal_actions": game.illegal_actions,
    }
