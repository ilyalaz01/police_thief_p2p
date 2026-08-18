# ADR-007: Official outer-series and shared-config boundary

Status: ACCEPTED

## Context

The accepted runtime and professor-compatible artifacts close one sub-game. The official Appendix
B/F contract instead fixes a six-sub-game series and a full schema-1.2 shared configuration. That
configuration, the flat fourteen professor terms, and the extended local `MatchProfile` have
different fields and serialization purposes. Combining them would change already verified bytes
and could produce a stable but cross-team-incompatible game UID.

The official source fixes series length, scores, game constants, and Gatekeeper minima. It does
not uniquely select a JSON whitespace profile, which group starts as Police, or how a tied series
applies the two-point award. Those differences remain negotiated.

## Decision

Add an outer, offline-only `league` package and `LeagueSDK` service. It does not modify or wrap the
single-game runtime. The package:

- validates the exact Appendix-B schema-1.2 field inventory, fixed values, positive negotiated
  inputs, and Table-19 minima;
- serializes a local candidate only under the named
  `appendix_b_canonical_compact_v1` proposal and labels it pending bilateral approval;
- produces a lock only when the peer names the same serialization profile and SHA-256 and the
  caller records explicit bilateral approval;
- derives series IDs from the flat fourteen terms with `num_games=6`, never the Appendix-B body;
- schedules six alternating roles only under an explicitly matching named schedule profile;
- validates complete eight-character identities and opaque Git commits for both groups in every
  sub-game; and
- aggregates official capture/survival scores but leaves equal-total settlement blocked until a
  bilateral tie policy is recorded.

The injected offline coordinator performs no transport, gameplay, Gmail, reporting, or
authorization side effect. A later adapter may call the accepted single-game runtime, but only
after separate localhost tests and without editing frozen game/wire semantics.

## Rejected alternatives

- Extending `MatchProfile.reference_terms()` to six games would break the proven one-game
  professor/self-test contract.
- Hashing the full Appendix-B object for `game_uid` would contradict the pinned flat-term join.
- Selecting pretty JSON, a starting role, or a tie interpretation silently would turn an
  interoperability difference into an invented rule.
- Adding league orchestration to the CLI or artifact builders would bypass the single SDK facade
  and risk changing pinned schema-1.1 builders.

## Consequences

The repository can now prepare and test an official series boundary offline while remaining
honest that no peer has approved its proposed bytes, schedule, identity, or tie scope. `LGE-001`
stays in progress until a six-sub-game localhost runtime/artifact adapter and full differential
evidence are accepted. Gmail, public transport, opponent contact, counted play, and final
reporting remain separately blocked.
