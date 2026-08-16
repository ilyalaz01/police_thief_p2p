# PRD: P2P Interoperability

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

## Background and I/O

Two isolated peers exchange signed negotiation objects and at-least-once turn/audit/control calls
over FastMCP. Inputs are a byte-locked `MatchProfile`, endpoint settings, identity, and turn/audit
objects. Outputs are queued messages, accepted ordered turns, deterministic failures, and redacted
operator results.

Requirements: `/mcp` and four reference tools; exact terms/profile validation; identical retry
payload; monotonic deadlines; same-step/same-commit absorption; equivocation rejection; bounded
future-step buffering; stale handling; no deadline extension from duplicates; URL validation and
redaction. Current `McpPeerClient` centralizes FastMCP calls, retry count/interval, and deadlines;
`PeerInboxes` uses `queue.Queue`.

## Selection, evidence, and gaps

The selected implemented approach is synchronous outbound FastMCP calls plus one daemon server
thread and four queues, coordinated by `PeerRuntime`. Evidence:
`tests/test_phase4a_runtime_network.py`, `tests/test_phase4a_runtime_rules.py`,
`tests/test_phase4b_network.py`, `tests/test_phase4b_identity_gates.py`, the
[Phase 4D1A test mapping](audits/PHASE4D1A_TEST_SPLIT.md), local/public phase reports, and
[interop decisions](INTEROP_DECISIONS.md). Alternatives—async orchestration, a generic API
gatekeeper, or brokered transport—remain unselected.

Rate limiting, bounded queue depth, backpressure, drain policy, and call monitoring are not
implemented. A future gatekeeper must not alter frozen deadline/retry/duplicate behavior.
Real-team fields and consensus require explicit bilateral approval; no readiness is claimed.

Metrics: profile mismatch rejected before play; duplicate/equivocation/window scenarios exact;
timeout within negotiated bound; no secret/hidden-state diagnostics; tool surface 4/4. Tests cover
malformed frames, retry exhaustion, transport loss, isolated processes, and redaction.

Definition of Done for a future change: ADR accepted, contract characterization tests first,
bounded-load tests, race review, existing transport/Hcommit/conformance/frozen checks green, and
human escalation on any semantic difference. Negotiated/frozen boundaries are defined by
[the authority baseline](../RULES_AND_INTEROP_BASELINE.md) and profiles.
