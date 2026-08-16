# Phase 4D1D — REF-001 Production Splits

Result: **GREEN**. REF-001 is complete. All project-authored Python modules under `src/` and
`tests/` now contain at most 150 nonblank/non-comment lines. This is a structural acceptance only;
it does not claim SDK, gatekeeper, configuration, release, real-team, or counted-match readiness.

## Commits and scope

- `689aac0` — `test: characterize phase3b policy contract`
- `cae53dd` — `refactor: split phase3b search helpers`
- `46844a8` — `test: characterize runtime module contract`
- `e4ef336` — `refactor: split peer runtime responsibilities`
- The documentation/governance commit records this report and the permanent line-limit gate.

No game rules, frozen champion, MatchProfile bytes, retry/deadline policy, turn protocol, crypto,
audit/replay semantics, schema 1.1 builders, consensus scope, external dependency, or public
operation was selected for change.

## Phase 3B characterization and split

The UTF-8 compact-JSON characterization is 48,145 bytes and hashes to
`6966c3d4694911039181bed20568832ee6f1228a636a3f5b7d141fb48bb70457`. It pins the public policy
imports and signatures, exact constructor failures, feature order, tactical output, diagnostics,
node counts, action scores/components/replies, and 27 deterministic combinations of opponent
model, belief usage, and search depth.

Models, reply enumeration, and scoring methods were extracted without changing the public classes
defined in `phase3b.py`. Counts are 130 for `phase3b.py`, 32 for `phase3b_models.py`, 71 for
`phase3b_replies.py`, 86 for `phase3b_scoring.py`, and 117 for the characterization test.

## Runtime characterization and split

The compact-JSON runtime contract is 2,327 bytes and hashes to
`fc86adbbc506b2edd489926a31b97fd2e56a781a9eeb1c29291e9a509d912f67`. It pins phases, constants,
public and private method signatures, dataclass signatures, profile conversion, action wire
objects, audit-result normalization, Git-provenance failures, and the exact Hebrew/emoji default.

`PeerRuntime` remains defined in `runtime.py`; existing compatibility imports and the module-local
`start_server` patch point remain available. Lifecycle, board, sending, audit, schema 1.1 artifact,
and model/conversion responsibilities moved to focused modules. Counts are 150 for `runtime.py`,
104 for `runtime_artifacts.py`, 96 for `runtime_audit.py`, 63 for `runtime_board.py`, 102 for
`runtime_lifecycle.py`, 75 for `runtime_models.py`, 103 for `runtime_sending.py`, and 95 for the
runtime characterization test.

An intermediate comparison found that a shell rendering had transformed the Unicode default.
The accepted Git baseline exposed the mismatch and the exact `שלום 🙂 localhost` value was restored
before acceptance. No distorted value was committed as an accepted implementation.

## Acceptance evidence

| Gate | Result |
|---|---|
| Full suite | PASS — 158/158; no skips or xfails |
| Configured branch coverage | PASS — 93.29% |
| Runtime-focused local peer/audit/artifact tests | PASS — 33/33 |
| Ruff `src tests` | PASS — zero errors |
| Hcommit golden vectors | PASS — 5/5 |
| Pinned conformance kit | PASS — 125/125 |
| Frozen production manifest | PASS — 7/7 exact |
| B0/B1 consensus/profile tests | PASS — 7/7 |
| Pinned-professor artifact differential | PASS — no skip |
| Independent line scan | PASS — 76 files, zero violations, maximum 150 |

The permanent governance test scans every Python file under `src/` and `tests/` using the same
nonblank/non-comment definition and fails on any count above 150. Historical phase audits remain
unchanged as point-in-time evidence.

No public network, tunnel, Gmail, opponent contact, gameplay, league reporting, counted match,
strategy experiment, new AI/ML, dependency, merge, push, or tag was performed.
