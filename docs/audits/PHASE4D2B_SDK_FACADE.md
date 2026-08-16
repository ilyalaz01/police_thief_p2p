# Phase 4D2B — Single SDK Facade

Result: **GREEN**. SDK-001 is complete. Every approved public business operation is reachable from
one root `PoliceThiefSDK`, and the tracked CLI contains argument handling plus one typed SDK
delegation. This acceptance does not claim Gatekeeper, GUI, real-team, public-network, or counted
readiness.

## Commits and TDD evidence

- `a0d78df` — `test: define single sdk entry point contract`
- The targeted RED run failed during collection because `PoliceThiefSDK` did not exist.
- `ed67b15` — `feat: add single sdk facade and cli delegation`
- `be54acf` — `test: complete sdk runtime operation inventory`
- The documentation/governance commit accepts ADR-003 and records this report.

## Accepted architecture

The root facade composes six stateless single-concern services: domain, policies, evaluation,
artifacts, transport, and configuration. Operations alias the established implementations, so
legacy signatures, exceptions, class identities, bytes, outputs, module patch points, and imports
remain compatible. No business implementation moved into the facade.

The CLI now creates `PeerLaunchRequest` and calls `PoliceThiefSDK.transport.launch_peer`. Config
mode matching, URL defaulting, profile timeout extraction, endpoint validation, and lower runtime
invocation moved behind that boundary without changing their order or errors. A permanent AST
regression rejects future CLI imports from business modules.

The inventory covers domain rules/simulation, every supported policy family and public diagnostic,
local evaluation, commit/reveal and audit/replay, all schema 1.1 builders and hash scopes, profile/
protocol/network/runtime operations, runtime conversions, and versioned configuration/scanning.
Future business operations must extend the relevant service and inventory test.

## Acceptance evidence

| Gate | Result |
|---|---|
| SDK/CLI/config focused tests | PASS — 18/18 |
| Full suite | PASS — 174/174; no skips or xfails |
| Configured branch coverage | PASS — 93.67% |
| Ruff `src tests` | PASS — zero errors |
| Hcommit golden vectors | PASS — 5/5 |
| Pinned conformance kit | PASS — 125/125 |
| Frozen production manifest | PASS — 7/7 exact |
| B0/B1 consensus/profile tests | PASS — 7/7 |
| Pinned-professor artifact differential | PASS — no skip |
| Legacy callable/class identity checks | PASS |
| Python 150-line gate | PASS — 87 files; maximum 150 |

No rule, policy, wire/profile byte, artifact byte, retry/deadline, dependency, public network,
tunnel, Gmail, opponent contact, gameplay, league reporting, counted match, or AI/ML/search work
occurred.
