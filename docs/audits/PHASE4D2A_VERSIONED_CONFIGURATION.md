# Phase 4D2A — Versioned Operational Configuration

Result: **GREEN**. CFG-001 is complete. The project now has a strict versioned startup metadata
boundary, a credential-free tracked example, and a sanitized secret scanner. This acceptance does
not claim SDK, Gatekeeper, real-team, public-network, or counted-match readiness.

## Commits and TDD evidence

- `e9f94a8` — `test: define versioned configuration contract`
- The targeted RED run failed during collection with
  `ModuleNotFoundError: police_thief_lab.configuration`.
- `0685780` — `feat: add versioned operational config gate`
- The documentation/governance commit records the accepted decision and this report.

The implementation adds `police_thief_lab.configuration`, the strict
`config/operational.self-test.v1.json` example, `.env-example`, CLI selection through
`--operational-config` or `POLICE_THIEF_CONFIG_PATH`, and 12 focused tests. No dependency changed.

## Accepted contract

The exact JSON fields are `schema_version`, `package_version`, `operation_mode`, `secret_source`,
and `retain_sensitive_values`. Schema 1.0 requires package 1.0.0, an operation mode of `offline`,
`self_test`, or `real_team`, `environment_only` secret sourcing, and disabled sensitive-value
retention. Missing/unknown fields, incompatible versions, unsafe sources, unsupported modes, and
malformed JSON fail closed.

When supplied to the peer CLI, configuration validation and mode matching complete before the
profile is read or peer objects are constructed. Omission retains the prior CLI behavior. The
scanner emits only path, line number, and category; synthetic tests prove that the matched value
is not returned.

Operational configuration contains no fixed rule, profile field, endpoint, credential, retry or
deadline, Gatekeeper policy, artifact value, tie, or consensus field. Loading it reproduces the
same MatchProfile bytes and SHA-256. `real_team` is classification, not authorization; `counted`
is not supported.

## Acceptance evidence

| Gate | Result |
|---|---|
| Focused configuration/preflight/profile/frozen tests | PASS — 20/20 |
| Full suite | PASS — 170/170; no skips or xfails |
| Configured branch coverage | PASS — 93.15% |
| Ruff `src tests` | PASS — zero errors |
| Hcommit golden vectors | PASS — 5/5 |
| Pinned conformance kit | PASS — 125/125 |
| Frozen production manifest | PASS — 7/7 exact |
| B0/B1 consensus/profile tests | PASS — 7/7 |
| Pinned-professor artifact differential | PASS — no skip |
| MatchProfile byte/hash comparison | PASS — exact before/after |
| Tracked config/environment secret scan | PASS — zero findings |

No public network, tunnel, Gmail, opponent contact, gameplay, league reporting, counted match,
strategy experiment, new AI/ML, dependency change, or external source modification occurred.
