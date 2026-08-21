"""Official outer-series operations exposed through the SDK."""

from ..league import (
    APPENDIX_B_CANONICAL_COMPACT_V1,
    APPENDIX_B_SCOPE,
    KIT_SORTED_FIRST_POLICE_ODD_V1,
    PENDING_BILATERAL_APPROVAL,
    AppendixBConfigCandidate,
    AppendixBConfigLock,
    HardwareIdentity,
    LocalhostSeriesRequest,
    LocalhostSeriesResult,
    SeriesSlot,
    TeamDeclarationIdentity,
    aggregate_series_rows,
    build_appendix_b_candidate,
    build_series_schedule,
    confirm_appendix_b_lock,
    coordinate_offline_series,
    derive_series_game_ids,
    load_declaration_identity,
    run_localhost_series,
    series_reference_terms,
    series_token_totals,
    validate_series_commits,
)


class LeagueSDK:
    """Stable access to offline series gates without arming league operations."""

    APPENDIX_B_CANONICAL_COMPACT_V1 = APPENDIX_B_CANONICAL_COMPACT_V1
    APPENDIX_B_SCOPE = APPENDIX_B_SCOPE
    KIT_SORTED_FIRST_POLICE_ODD_V1 = KIT_SORTED_FIRST_POLICE_ODD_V1
    PENDING_BILATERAL_APPROVAL = PENDING_BILATERAL_APPROVAL
    AppendixBConfigCandidate = AppendixBConfigCandidate
    AppendixBConfigLock = AppendixBConfigLock
    HardwareIdentity = HardwareIdentity
    LocalhostSeriesRequest = LocalhostSeriesRequest
    LocalhostSeriesResult = LocalhostSeriesResult
    SeriesSlot = SeriesSlot
    TeamDeclarationIdentity = TeamDeclarationIdentity
    aggregate_series_rows = staticmethod(aggregate_series_rows)
    build_appendix_b_candidate = staticmethod(build_appendix_b_candidate)
    build_series_schedule = staticmethod(build_series_schedule)
    confirm_appendix_b_lock = staticmethod(confirm_appendix_b_lock)
    coordinate_offline_series = staticmethod(coordinate_offline_series)
    derive_series_game_ids = staticmethod(derive_series_game_ids)
    load_declaration_identity = staticmethod(load_declaration_identity)
    series_reference_terms = staticmethod(series_reference_terms)
    series_token_totals = staticmethod(series_token_totals)
    run_localhost_series = staticmethod(run_localhost_series)
    validate_series_commits = staticmethod(validate_series_commits)
