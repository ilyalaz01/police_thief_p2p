# Phase 4D4 — Concurrency, Lifecycle, and Capacity

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Status: **GREEN** for CON-001 only. This phase does not claim release, real-team, uncounted-warm-up,
or counted-match readiness.

## Accepted change

- Serialized Gatekeeper admission and closure under one state lock, preventing a call from being
  queued after shutdown has already drained and removed its workers.
- Counted accepted work across the queue-to-worker transition, eliminating false-empty drain
  observations.
- Made closed workers self-reap after outstanding calls finish, including after the owner's bounded
  `close()` call has visibly timed out.
- Proved the exact accepted outbound capacity is `concurrent_max + queue_max`; the next immediate
  call receives explicit backpressure.
- Documented peer-process, FastMCP-server, inbox, Gatekeeper, worker, lock, exception, and cleanup
  ownership without changing the public transport or wire contract.

## RED and GREEN evidence

The focused RED commit produced one pass and two intentional failures: the capacity contract was
already true, while the execute/close race stranded a caller and a timed-out close left its worker
alive. The GREEN implementation produced 3/3 passing focused lifecycle tests. Existing
Gatekeeper/configuration compatibility tests then produced 16/16 passes with Ruff clean.

## Final acceptance evidence

| Gate | Result |
|---|---|
| Focused lifecycle contracts | PASS — 3/3 |
| Existing Gatekeeper/config compatibility | PASS — 16/16 |
| Full pytest | PASS — 198/198; no skips or xfails |
| Branch coverage | PASS — 94.07%; threshold 85% |
| Ruff `src tests` | PASS — zero errors |
| Hcommit golden vectors | PASS — 5/5 |
| Pinned conformance kit | PASS — 125/125 |
| Frozen production manifest | PASS — 7/7 exact |
| Python 150-line regression | PASS — no project violation |
| Retained-evidence scan | PASS — 3 files, zero findings; JSON valid |

The full suite also retained the pinned-professor artifact differential without a skip. The
machine-readable companion records the measured counts and operation exclusions without raw
stdout/stderr, payloads, endpoints, credentials, nonces, or external identities.

## Scope and blockers

The FastMCP server remains intentionally owned by peer-process lifetime; this phase does not add or
claim an in-process server restart API. No game rule, observation, policy, profile, wire frame,
retry/deadline rule, artifact, consensus serialization, Rule 47 behavior, or frozen hash changed.

No partner-owned release-engineering path, public network, tunnel, gameplay, Gmail, external-team
contact, league reporting, counted match, strategy experiment, or new AI/ML/search work occurred.
Real-team play remains blocked on the release workstream plus actual bilateral identities/commit
values, stable endpoints, and explicit Rule 47 and consensus/tie-scope agreement.
