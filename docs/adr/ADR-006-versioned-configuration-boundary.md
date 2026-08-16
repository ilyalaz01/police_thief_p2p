# ADR-006: Versioned configuration boundary

Status: ACCEPTED

## Context

`pyproject.toml` and package `__version__` report 1.0.0, while profile and fixture schemas have
separate higher-authority byte contracts. Operational startup metadata needed a strict versioned
boundary without turning fixed game or interoperability values into operator options.

## Decision

Use a dependency-free JSON loader for a closed schema with exactly these fields:

- `schema_version`: loader schema, currently `1.0`;
- `package_version`: must equal the installed package version, currently `1.0.0`;
- `operation_mode`: one of `offline`, `self_test`, or `real_team`;
- `secret_source`: must be `environment_only`;
- `retain_sensitive_values`: must be `false`.

The peer CLI accepts an optional `--operational-config` path or the
`POLICE_THIEF_CONFIG_PATH` environment variable. It validates the file and its mode before reading
the match profile, constructing endpoints, or invoking the peer. Supplying no config preserves the
existing CLI contract. A config declares startup intent; it does not authorize network activity,
real-team contact, league reporting, or counted play.

The loader rejects malformed JSON, missing or unknown fields, unsupported schemas or modes,
package-version mismatch, non-environment secret sources, and sensitive-value retention. The
repository includes a self-test example and an intentionally credential-free `.env-example`.
Secret scanning reports only path, line, and category; it never returns a detected value.

## Boundaries

Operational configuration must not contain game constants, negotiated terms, transport URLs,
credentials, Gatekeeper policy, or artifact/consensus fields. It remains outside `MatchProfile`
serialization, config hashes, game UID derivation, frozen policies, and the seven-file frozen
manifest. `counted` is deliberately not a supported operation mode.

No new dependency is introduced and no automatic `.env` loading occurs. Future schema fields or
migrations require a new reviewed decision and compatibility tests. Gatekeeper/rate/queue design
remains owned by ADR-004 and API-001.

## Evidence

Phase 4D2A used a committed RED test followed by the implementation. Its acceptance evidence is
recorded in [the audit](../audits/PHASE4D2A_VERSIONED_CONFIGURATION.md): 170/170 tests, 93.15%
branch coverage, Ruff clean, Hcommit 5/5, conformance 125/125, frozen manifest 7/7, and exact
MatchProfile byte/hash preservation.
