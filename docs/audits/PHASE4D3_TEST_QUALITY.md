# Phase 4D3 — Layered Tests and Quality Evidence

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Status: **GREEN** for TST-001 and QLT-001 only. This phase does not claim release, real-team,
uncounted-warm-up, or counted-match readiness.

## Accepted change

- Reorganized the existing deterministic suite into documented `unit`, `integration`, and
  `system` boundaries; reserved `tests/offline_ops/` for the partner-owned release workstream.
- Added shared fixtures, stable project paths, support-module placement, and automatic pytest
  layer markers.
- Preserved all 187 pre-existing test IDs. A basename-plus-node normalized comparison produced
  187 entries on each side and identical SHA-256
  `ea5099929541c00e8f666c8d76bfd7f2570ac3cb6d5819adbd649fa432f266e6`.
- Added four test-architecture contracts and three quality-evidence contracts.
- Added a source-to-test map, critical-path success/failure map, and sanitized report-retention
  policy.

## RED evidence

| Contract | Expected RED result | Resolution |
|---|---|---|
| Layered architecture | 4 failed: layers, flat tests, root helpers, missing map | Mechanical moves, shared support/fixtures, `docs/TESTING.md` |
| Quality evidence | 3 failed: missing path map, retention policy, audit JSON | Added mapped cases, policy, and this reviewed evidence pair |
| Ruff preflight | 1 unused-import error in the new quality contract | Removed the import; linked zero-error rerun recorded below |

The failed outputs were not retained verbatim. Only counts and non-sensitive failure categories
are retained here; the linked GREEN runs supersede them without erasing the RED history.

## Acceptance evidence

| Gate | Result |
|---|---|
| Full pytest | PASS — 194/194, no skips or xfails |
| Branch coverage | PASS — 93.91%, threshold 85% |
| Ruff `src tests` | PASS — zero errors |
| Existing collection preservation | PASS — 187/187 normalized IDs and identical SHA-256 |
| New governance tests | PASS — 7/7 |
| Hcommit | PASS — 5/5 |
| Conformance kit | PASS — 125/125 |
| Frozen manifest | PASS — 7/7 |
| 150-line regression | PASS — no project Python violation |
| Retained-evidence scan | PASS — 5 files, zero findings, JSON valid |

The machine-readable companion records commands, counts, and operation exclusions without raw
stdout/stderr, match payloads, endpoints, credentials, nonces, or external identities.

## Scope and blockers

No production source, frozen file, game rule, strategy, profile, serialization, retry/deadline,
artifact, or interoperability semantic changed. No public network, tunnel, gameplay, Gmail,
external-team contact, league reporting, or counted operation occurred.

Release Engineering RE-001 remains partner-owned and separate. Real-team play remains blocked on
that workstream plus actual bilateral identities/commit values, stable endpoints, and explicit
agreement on Rule 47 and consensus/tie scope.
