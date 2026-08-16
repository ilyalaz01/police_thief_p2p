"""Golden tests for the negotiated reference scent profile."""

import json

import pytest

from police_thief_lab import Position, ReferenceSubtractiveChebyshevV1
from police_thief_lab.scent import scent_model_for
from tests.support.project_paths import PROJECT_ROOT

FIXTURE = PROJECT_ROOT / "interop" / "fixtures" / "scent_reference_scenarios.json"


def _matrix(field: tuple[tuple[Position, float], ...], size: int = 7) -> list[list[float]]:
    values = dict(field)
    return [[values.get(Position(row, col), 0.0) for col in range(size)] for row in range(size)]


def test_center_deposit_then_decay_matches_golden_vector() -> None:
    """The first transmitted field has the fixture's 0.8 center and ring values."""
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    model = ReferenceSubtractiveChebyshevV1()
    field = model.advance((), Position(3, 3), 7)
    assert _matrix(field) == fixture["scenarios"]["one_decay"]


@pytest.mark.parametrize(
    ("center", "fixture_name"),
    [
        (Position(0, 0), "edge_0_0"),
        (Position(0, 6), "edge_0_6"),
        (Position(6, 0), "edge_6_0"),
        (Position(6, 6), "edge_6_6"),
    ],
)
def test_edges_clip_against_golden_vectors(center: Position, fixture_name: str) -> None:
    """Reference emission clips cleanly at every board corner."""
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    field = ReferenceSubtractiveChebyshevV1().advance((), center, 7)
    assert _matrix(field) == fixture["scenarios"][fixture_name]


def test_stay_redeposit_is_deterministic() -> None:
    """STAY emits and max-merge makes repeated same-center updates stable."""
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    model = ReferenceSubtractiveChebyshevV1()
    field = model.advance((), Position(3, 3), 7)
    field = model.advance(field, Position(3, 3), 7)
    assert _matrix(field) == fixture["scenarios"]["repeat_same_center"]


@pytest.mark.parametrize(
    ("centers", "fixture_name"),
    [
        ((Position(3, 3), Position(3, 4)), "move_east"),
        ((Position(3, 3),) * 5, "stay_five"),
        ((Position(3, 3),) * 25, "twenty_five_updates"),
    ],
)
def test_reference_update_sequences_match_golden_vectors(
    centers: tuple[Position, ...], fixture_name: str
) -> None:
    """Movement, repeated STAY, and long-run updates match generated fixtures."""
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    model = ReferenceSubtractiveChebyshevV1()
    field = ()
    for center in centers:
        field = model.advance(field, center, 7)
    assert _matrix(field) == fixture["scenarios"][fixture_name]


def test_unknown_scent_dialect_is_not_silently_collapsed() -> None:
    """A negotiated but unsupported profile fails loudly at selection."""
    with pytest.raises(ValueError, match="unsupported scent profile"):
        scent_model_for("multiplicative_book_v1")
