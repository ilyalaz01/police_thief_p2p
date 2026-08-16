"""Local deterministic evaluation operations exposed through the SDK."""

from ..evaluation import (
    AblatedBackend,
    BatchResult,
    GameResult,
    LaggedScentBackend,
    PolicyFactory,
    ScentAblation,
    cross_play,
    markdown_matrix,
    run_batch,
    run_game,
    write_json,
)


class EvaluationSDK:
    """Stable access to single-game, batch, matrix, and rendering operations."""

    AblatedBackend = AblatedBackend
    BatchResult = BatchResult
    GameResult = GameResult
    LaggedScentBackend = LaggedScentBackend
    PolicyFactory = PolicyFactory
    ScentAblation = ScentAblation
    cross_play = staticmethod(cross_play)
    markdown_matrix = staticmethod(markdown_matrix)
    run_batch = staticmethod(run_batch)
    run_game = staticmethod(run_game)
    write_json = staticmethod(write_json)
