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
thread and four bounded queues, coordinated by the public `PeerRuntime` assembled from
responsibility mixins. Every outbound discovery/tool attempt passes through one process-wide
versioned `ApiGatekeeper`; the Gatekeeper provides FIFO admission, rate windows, bounded
backpressure, drain, and value-free monitoring while `McpPeerClient` retains the frozen retry and
deadline semantics. Evidence: `tests/integration/test_interop/test_phase4a_runtime_network.py`,
`tests/integration/test_interop/test_phase4a_runtime_rules.py`,
`tests/integration/test_interop/test_phase4b_network.py`,
`tests/integration/test_interop/test_phase4b_identity_gates.py`, the
[Phase 4D1A test mapping](audits/PHASE4D1A_TEST_SPLIT.md), local/public phase reports, and
[interop decisions](INTEROP_DECISIONS.md). Phase 4D2C and Phase 4D4 provide the Gatekeeper and
concurrency evidence. Alternatives—async orchestration or brokered transport—remain unselected.

Phase 4D13B proves the six-slot adapter with twelve independent loopback peer processes, six
successful games, twelve audits/replays, and two checker-accepted artifact sets. Real operator
inputs and bilateral approvals remain incomplete under `LGE-001`/`HUM-001`. The full Appendix-B
candidate, flat 14-term domain, and schema-1.1 reference bodies remain separate.
Real-team fields and consensus still require explicit bilateral approval, and Gmail reporting is
separately blocked under `MAIL-001`; no counted readiness is claimed.

Metrics: profile mismatch rejected before play; duplicate/equivocation/window scenarios exact;
timeout within negotiated bound; no secret/hidden-state diagnostics; tool surface 4/4. Tests cover
malformed frames, retry exhaustion, transport loss, isolated processes, and redaction.

Definition of Done for a future change: ADR accepted, contract characterization tests first,
bounded-load tests, race review, existing transport/Hcommit/conformance/frozen checks green, and
human escalation on any semantic difference. The existing Gatekeeper/concurrency implementation
already meets that contract for FastMCP. Negotiated/frozen boundaries are defined by
[the authority baseline](../RULES_AND_INTEROP_BASELINE.md) and profiles.
