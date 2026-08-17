"""Deterministic summary, uncertainty, and elementary-effect calculations."""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any


def wilson_interval(
    successes: int, total: int, z: float = 1.959963984540054
) -> tuple[float, float]:
    """Return the Wilson score interval for a binomial proportion."""
    if total < 1:
        raise ValueError("Wilson interval requires at least one observation")
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(
        proportion * (1 - proportion) / total + z * z / (4 * total * total)
    ) / denominator
    return centre - radius, centre + radius


def summarize(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate public rows by setting and policy pairing in stable order."""
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        grouped[(row["setting"], row["police_policy"], row["thief_policy"])].append(row)
    return [_summary(rows) for rows in grouped.values()]


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate one pairing/setting summary with paired-seed variance."""
    captures = sum(row["captured"] for row in rows)
    low, high = wilson_interval(captures, len(rows))
    by_seed: dict[int, list[bool]] = defaultdict(list)
    for row in rows:
        by_seed[row["seed"]].append(row["captured"])
    seed_rates = [statistics.fmean(values) for values in by_seed.values()]
    first = rows[0]
    return {
        "setting": first["setting"],
        "factor": first["factor"],
        "factor_value": first["factor_value"],
        "board_size": first["board_size"],
        "survival_threshold": first["survival_threshold"],
        "police_policy": first["police_policy"],
        "thief_policy": first["thief_policy"],
        "games": len(rows),
        "capture_rate": _round(captures / len(rows)),
        "wilson_95_low": _round(low),
        "wilson_95_high": _round(high),
        "capture_rate_variance_across_seeds": _round(statistics.pvariance(seed_rates)),
        "mean_police_score": _mean(rows, "police_score"),
        "mean_thief_score": _mean(rows, "thief_score"),
        "mean_police_actions": _mean(rows, "police_actions"),
        "mean_thief_actions": _mean(rows, "thief_actions"),
        "mean_barriers_placed": _mean(rows, "barriers_placed"),
        "illegal_action_count": sum(row["illegal_actions"] for row in rows),
    }


def effects(summary: list[dict[str, Any]], design: dict[str, Any]) -> list[dict[str, Any]]:
    """Compute paired capture deltas and per-unit OAT elementary effects."""
    baseline_id = design["method"]["baseline"]
    baseline = {
        (row["police_policy"], row["thief_policy"]): row
        for row in summary
        if row["setting"] == baseline_id
    }
    output = []
    for row in summary:
        if row["setting"] == baseline_id:
            continue
        reference = baseline[(row["police_policy"], row["thief_policy"])]
        base_value = 7 if row["factor"] == "board_size" else 35
        delta = row["capture_rate"] - reference["capture_rate"]
        output.append({
            "setting": row["setting"],
            "factor": row["factor"],
            "factor_value": row["factor_value"],
            "police_policy": row["police_policy"],
            "thief_policy": row["thief_policy"],
            "paired_capture_delta_from_baseline": _round(delta),
            "elementary_effect_per_parameter_unit": _round(
                delta / (row["factor_value"] - base_value)
            ),
        })
    return output


def _mean(rows: list[dict[str, Any]], key: str) -> float:
    """Return a consistently rounded arithmetic mean for one numeric field."""
    return _round(statistics.fmean(row[key] for row in rows))


def _round(value: float) -> float:
    """Round derived floats so serialized evidence is stable and readable."""
    return round(value, 8)
