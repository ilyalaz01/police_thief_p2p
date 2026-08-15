"""Replaceable scent models and the verified reference-v3 dialect."""

from __future__ import annotations

from typing import Protocol

from .models import Position, ScentField


class ScentModel(Protocol):
    """Advance one role's own scent field after that role acts."""

    name: str

    def advance(self, field: ScentField, center: Position, board_size: int) -> ScentField:
        """Deposit at the post-action position and perform the model update."""
        ...


class ReferenceSubtractiveChebyshevV1:
    """Verified `subtractive_chebyshev_v1` reference profile."""

    name = "subtractive_chebyshev_v1"
    field_size = 5
    intensity = 0.9
    decay = 0.1

    def advance(self, field: ScentField, center: Position, board_size: int) -> ScentField:
        """Max-merge Chebyshev rings, then subtract 0.1 and round to 3 decimals."""
        values = dict(field)
        half = self.field_size // 2
        falloff = self.intensity / (half + 1)
        for row_delta in range(-half, half + 1):
            for col_delta in range(-half, half + 1):
                position = Position(center.row + row_delta, center.col + col_delta)
                if 0 <= position.row < board_size and 0 <= position.col < board_size:
                    distance = max(abs(row_delta), abs(col_delta))
                    deposit = round(max(0.0, self.intensity - falloff * distance), 3)
                    values[position] = max(values.get(position, 0.0), deposit)
        decayed = {
            position: round(max(0.0, value - self.decay), 3)
            for position, value in values.items()
            if round(max(0.0, value - self.decay), 3) > 0.0
        }
        return tuple(sorted(decayed.items()))


def scent_model_for(profile: str) -> ScentModel:
    """Resolve a declared profile without silently accepting an unknown dialect."""
    if profile == ReferenceSubtractiveChebyshevV1.name:
        return ReferenceSubtractiveChebyshevV1()
    raise ValueError(f"unsupported scent profile: {profile}")
