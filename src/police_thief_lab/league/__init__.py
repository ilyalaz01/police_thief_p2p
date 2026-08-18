"""Official outer-series contracts kept separate from single-game interoperability."""

from .config import (
    APPENDIX_B_CANONICAL_COMPACT_V1,
    APPENDIX_B_SCOPE,
    PENDING_BILATERAL_APPROVAL,
    AppendixBConfigCandidate,
    AppendixBConfigLock,
    build_appendix_b_candidate,
    confirm_appendix_b_lock,
)
from .identity import HardwareIdentity, TeamDeclarationIdentity, validate_series_commits
from .series import (
    KIT_SORTED_FIRST_POLICE_ODD_V1,
    SeriesSlot,
    aggregate_series_rows,
    build_series_schedule,
    coordinate_offline_series,
    derive_series_game_ids,
    series_reference_terms,
    series_token_totals,
)

__all__ = [
    "APPENDIX_B_CANONICAL_COMPACT_V1",
    "APPENDIX_B_SCOPE",
    "KIT_SORTED_FIRST_POLICE_ODD_V1",
    "PENDING_BILATERAL_APPROVAL",
    "AppendixBConfigCandidate",
    "AppendixBConfigLock",
    "HardwareIdentity",
    "SeriesSlot",
    "TeamDeclarationIdentity",
    "aggregate_series_rows",
    "build_appendix_b_candidate",
    "build_series_schedule",
    "confirm_appendix_b_lock",
    "coordinate_offline_series",
    "derive_series_game_ids",
    "series_reference_terms",
    "series_token_totals",
    "validate_series_commits",
]
