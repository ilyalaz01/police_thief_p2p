"""Public local batch-evaluation API."""

from .ablations import AblatedBackend, LaggedScentBackend, ScentAblation
from .matrix import cross_play, markdown_matrix, write_json
from .models import BatchResult, GameResult
from .runner import PolicyFactory, run_batch, run_game

__all__ = [
    "BatchResult",
    "AblatedBackend",
    "GameResult",
    "LaggedScentBackend",
    "PolicyFactory",
    "ScentAblation",
    "cross_play",
    "markdown_matrix",
    "run_batch",
    "run_game",
    "write_json",
]
