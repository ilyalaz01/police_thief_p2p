"""Deterministic batch and cross-play aggregation tests."""

from police_thief_lab import GameConfig, Position
from police_thief_lab.evaluation import cross_play, markdown_matrix, run_batch
from police_thief_lab.policies import RandomLegalPolice, RandomLegalThief, SpaceSeekingThief


def _batch():
    configs = (("default", GameConfig()),)
    return run_batch(
        configs,
        range(5),
        RandomLegalPolice,
        RandomLegalThief,
        "RandomLegalPolice",
        "RandomLegalThief",
    )


def test_batch_seed_reproducibility() -> None:
    """Game records and deterministic metrics reproduce; wall-clock throughput is excluded."""
    left, right = _batch(), _batch()
    assert left.games == right.games
    deterministic_keys = set(left.metrics) - {"games_per_second"}
    assert {key: left.metrics[key] for key in deterministic_keys} == {
        key: right.metrics[key] for key in deterministic_keys
    }


def test_batch_aggregation_is_consistent() -> None:
    """Rates, scores, terminal counts, and illegal counts match constituent games."""
    batch = _batch()
    assert batch.metrics["games"] == 5
    assert batch.metrics["capture_rate"] + batch.metrics["survival_rate"] == 1
    assert sum(batch.metrics["terminal_reasons"].values()) == 5
    assert batch.metrics["police_score"] == sum(game.police_score for game in batch.games)
    assert batch.metrics["illegal_action_count"] == 0


def test_cross_play_uses_the_same_scenarios_and_seed_sets() -> None:
    """Every pairing receives an identical paired experimental design."""
    configs = (
        ("default", GameConfig()),
        ("opposite", GameConfig(police_start=Position(6, 6), thief_start=Position(0, 0))),
    )
    results = cross_play(
        configs,
        (3, 4),
        {"random": RandomLegalPolice},
        {"random": RandomLegalThief, "space": SpaceSeekingThief},
    )
    assert len(results) == 2
    expected = {(scenario, seed) for scenario, _ in configs for seed in (3, 4)}
    assert all(
        {(game.scenario, game.seed) for game in result.games} == expected for result in results
    )
    assert "| random |" in markdown_matrix(results)
