# Phase 4D2C — FastMCP API Gatekeeper

Result: **GREEN**. API-001 is complete for the current production external-call inventory. Every
outbound FastMCP attempt passes through versioned centralized admission/rate/queue/monitoring, and
inbound peer queues are bounded FIFO with blocking backpressure. This does not authorize or claim
public, external-team, warm-up, or counted operation readiness.

## Commits and TDD evidence

- `73a21a8` — `test: define centralized gatekeeper contract`
- The targeted RED run failed during collection because `police_thief_lab.gatekeeper` did not exist.
- `3e8ff80` — `feat: gate all outbound FastMCP calls`
- `c06debe` — `feat: bound peer inboxes with fifo backpressure`
- `c46bea2` — `test: cover gatekeeper configuration failures`
- `0f5f566` — `test: scan tracked rate policy for secrets`
- The documentation/governance commit accepts ADR-004 and records this report.

## Applicability and controls

The code inventory found two outbound FastMCP call sites: tool discovery and `McpPeerClient`
invocation. Both now execute through the process-wide `ApiGatekeeper`; no other production external
API client exists. The strict `config/rate_limits.v1.json` supplies minute/hour limits, one-worker
ordering, outbound waiting depth, inbound mailbox depth, and bounded monitoring retention.

The Gatekeeper queues FIFO until configured capacity, signals explicit backpressure only when full,
enforces rates before every attempt, drains completed work, and exposes count-only status. Metrics
retain only operation, success/failure, duration, and exception type. Request/response arguments are
cleared immediately after delivery and are absent from metrics/status.

The original `McpPeerClient` still owns exact retry count, interval, monotonic deadline,
deep-copied identical redelivery, attempt timing, and exhaustion text. Each retry is separately
gated and monitored. This preserves the higher-authority transport contract instead of introducing
a second retry policy.

Inbound FastMCP handlers use blocking `put` into configured bounded queues. The deterministic load
test proves a second message waits, the first is drained first, the second is then delivered, and
neither is dropped or reordered.

## Acceptance evidence

| Gate | Result |
|---|---|
| Gatekeeper/config/transport focused tests | PASS — 29/29 |
| Full suite | PASS — 187/187; no skips or xfails |
| Configured branch coverage | PASS — 93.91% |
| Ruff `src tests` | PASS — zero errors |
| Hcommit golden vectors | PASS — 5/5 |
| Pinned conformance kit | PASS — 125/125 |
| Frozen production manifest | PASS — 7/7 exact |
| B0/B1 consensus/profile tests | PASS — 7/7 |
| Pinned-professor artifact differential | PASS — no skip |
| Python 150-line gate | PASS — 92 files; maximum 150 |
| Tracked config/security scan | PASS — zero findings |

The suite performed deterministic simulator and localhost interoperability tests only. No public
transport, tunnel, external-team contact, Gmail, operational warm-up, league reporting, counted
match, strategy experiment, new AI/ML/search, or dependency change occurred.
